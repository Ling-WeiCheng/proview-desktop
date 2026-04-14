import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

import requests
from requests.structures import CaseInsensitiveDict


def request_with_curl_fallback(
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    params=None,
    data: Optional[Dict] = None,
    json_body: Optional[Dict] = None,
    timeout: int = 20,
    trust_env: bool = True,
):
    try:
        session = requests.Session()
        session.trust_env = trust_env
        return session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_body,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        if not _should_try_curl(exc):
            raise
        return _request_via_curl(
            method=method,
            url=url,
            headers=headers or {},
            params=params,
            data=data,
            json_body=json_body,
            timeout=timeout,
            trust_env=trust_env,
        )


def _should_try_curl(exc: Exception) -> bool:
    curl_path = shutil.which("curl.exe") or shutil.which("curl")
    if not curl_path:
        return False

    message = str(exc).lower()
    retryable_markers = (
        "ssl",
        "tls",
        "unexpected eof",
        "connection aborted",
        "connection reset",
        "eof occurred in violation of protocol",
        "timed out",
        "timeout",
        "proxy",
        "tunnel connection failed",
    )
    return any(marker in message for marker in retryable_markers)


def _request_via_curl(
    method: str,
    url: str,
    *,
    headers: Dict[str, str],
    params=None,
    data: Optional[Dict] = None,
    json_body: Optional[Dict] = None,
    timeout: int = 20,
    trust_env: bool = True,
):
    curl_path = shutil.which("curl.exe") or shutil.which("curl")
    if not curl_path:
        raise RuntimeError("curl is not available")

    request_url = requests.Request(method=method.upper(), url=url, params=params).prepare().url

    with tempfile.NamedTemporaryFile(delete=False) as header_file, tempfile.NamedTemporaryFile(delete=False) as body_file:
        header_path = Path(header_file.name)
        body_path = Path(body_file.name)

    command = [
        curl_path,
        "--silent",
        "--show-error",
        "--location",
        "--request",
        method.upper(),
        "--max-time",
        str(timeout),
        "--dump-header",
        str(header_path),
        "--output",
        str(body_path),
    ]

    try:
        if not trust_env:
            command.append("--noproxy")
            command.append("*")

        for key, value in headers.items():
            command.extend(["-H", f"{key}: {value}"])

        if json_body is not None:
            if not any(key.lower() == "content-type" for key in headers):
                command.extend(["-H", "Content-Type: application/json"])
            command.extend(["--data-binary", json.dumps(json_body, ensure_ascii=False)])
        elif data:
            for key, value in data.items():
                command.extend(["--data-urlencode", f"{key}={value}"])

        command.append(request_url)
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=timeout + 5,
            check=False,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(stderr or f"curl exited with status {result.returncode}")

        raw_headers = header_path.read_text(encoding="iso-8859-1", errors="replace")
        content = body_path.read_bytes()
        status_code, response_headers = _parse_curl_headers(raw_headers)
        return FallbackResponse(
            status_code=status_code,
            headers=response_headers,
            content=content,
            url=request_url,
        )
    finally:
        header_path.unlink(missing_ok=True)
        body_path.unlink(missing_ok=True)


def _parse_curl_headers(raw_headers: str):
    blocks = [block for block in re.split(r"\r?\n\r?\n", raw_headers) if block.strip()]
    if not blocks:
        return 0, CaseInsensitiveDict()

    header_lines = blocks[-1].splitlines()
    status_line = next((line for line in header_lines if line.startswith("HTTP/")), "")
    try:
        status_code = int(status_line.split()[1])
    except (IndexError, ValueError):
        status_code = 0

    headers = CaseInsensitiveDict()
    for line in header_lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()

    return status_code, headers


@dataclass
class FallbackResponse:
    status_code: int
    headers: CaseInsensitiveDict
    content: bytes
    url: str

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    @property
    def text(self) -> str:
        return self.content.decode(_get_encoding(self.headers), errors="replace")

    def json(self):
        return json.loads(self.text)

    def raise_for_status(self):
        if self.ok:
            return
        raise requests.HTTPError(
            f"{self.status_code} Error for url: {self.url}",
            response=self,
        )


def _get_encoding(headers: CaseInsensitiveDict) -> str:
    content_type = headers.get("Content-Type", "")
    for part in _split_header_parts(content_type):
        if part.lower().startswith("charset="):
            return part.split("=", 1)[1].strip() or "utf-8"
    return "utf-8"


def _split_header_parts(value: str) -> Iterable[str]:
    return [part.strip() for part in value.split(";") if part.strip()]
