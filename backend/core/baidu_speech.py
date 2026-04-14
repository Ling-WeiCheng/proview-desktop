"""
百度语音 API 客户端
- STT: 语音识别 REST API (短语音识别)
- TTS: 短文本在线合成 REST API
"""

import os
import json
import time
import base64
import urllib.parse
import requests

from utils.http_fallback import request_with_curl_fallback


class BaiduSpeechClient:
    """百度语音 API 封装（Token 管理 + STT + TTS）"""

    TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    TTS_URL = "https://tsn.baidu.com/text2audio"
    ASR_URL = "https://vop.baidu.com/server_api"

    def __init__(self, app_key: str, secret_key: str, cuid: str = "proview_demo"):
        self.app_key = app_key
        self.secret_key = secret_key
        self.cuid = cuid
        self._access_token = None
        self._token_expires_at = 0

    @property
    def access_token(self) -> str:
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token
        self._refresh_token()
        return self._access_token

    def _refresh_token(self):
        resp = request_with_curl_fallback(
            "POST",
            self.TOKEN_URL,
            params={
                "grant_type": "client_credentials",
                "client_id": self.app_key,
                "client_secret": self.secret_key,
            },
            timeout=10,
            trust_env=False,
        )
        resp.raise_for_status()
        data = resp.json()
        if "access_token" not in data:
            raise RuntimeError(f"获取百度 Token 失败: {data}")
        self._access_token = data["access_token"]
        self._token_expires_at = time.time() + data.get("expires_in", 2592000) - 60
        print(f"[OK] Baidu access_token refreshed, expires_in={data.get('expires_in', 0)}s")

    # ── TTS: 文本 → 音频 ──────────────────────────────
    def text_to_speech(
        self, text: str, *, per: int = 4115, spd: int = 5,
        pit: int = 5, vol: int = 5, aue: int = 4
    ) -> bytes:
        """
        短文本在线合成，返回音频二进制数据。
        per: 发音人（4115=度小贤臻品, 0=女声, 1=男声, 5003=度逍遥精品）
        aue: 3=mp3, 4=pcm-16k, 6=wav
        """
        # 百度要求 tex 做 2 次 urlencode，requests.post(data=) 会自动做 1 次，
        # 所以这里手动做 1 次即可
        tex = urllib.parse.quote_plus(text)
        payload = {
            "tex": tex,
            "tok": self.access_token,
            "cuid": self.cuid,
            "ctp": 1,
            "lan": "zh",
            "spd": spd,
            "pit": pit,
            "vol": vol,
            "per": per,
            "aue": aue,
        }
        print(f"  [DEBUG TTS] text={text[:50]}... per={per} aue={aue}")
        resp = request_with_curl_fallback(
            "POST",
            self.TTS_URL,
            data=payload,
            timeout=30,
            trust_env=False,
        )
        content_type = resp.headers.get("Content-Type", "")
        print(f"  [DEBUG TTS] status={resp.status_code} Content-Type={content_type} size={len(resp.content)}")
        if content_type.startswith("audio"):
            return resp.content
        # 合成失败，返回的是 JSON 错误
        try:
            err = resp.json()
        except Exception:
            err = resp.text[:200]
        raise RuntimeError(f"TTS 合成失败: {err}")

    # ── STT: 音频 → 文本 ──────────────────────────────
    def speech_to_text(
        self, audio_data: bytes, *, fmt: str = "pcm", rate: int = 16000
    ) -> str:
        """
        短语音识别，返回识别文本。
        audio_data: pcm/wav/amr 二进制
        fmt: pcm / wav / amr
        rate: 采样率，固定 16000
        """
        speech_b64 = base64.b64encode(audio_data).decode("utf-8")
        payload = {
            "format": fmt,
            "rate": rate,
            "channel": 1,
            "cuid": self.cuid,
            "token": self.access_token,
            "speech": speech_b64,
            "len": len(audio_data),
        }
        print(f"  [DEBUG STT] fmt={fmt} rate={rate} audio_len={len(audio_data)} b64_len={len(speech_b64)}")
        resp = request_with_curl_fallback(
            "POST",
            self.ASR_URL,
            json_body=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
            trust_env=False,
        )
        print(f"  [DEBUG STT] status={resp.status_code} url={resp.url}")
        resp.raise_for_status()
        data = resp.json()
        print(f"  [DEBUG STT] response={json.dumps(data, ensure_ascii=False)[:300]}")
        if data.get("err_no") == 0:
            return data["result"][0]
        raise RuntimeError(f"STT 识别失败: err_no={data.get('err_no')}, msg={data.get('err_msg')}")


def test_api():
    """
    独立测试函数，逐步验证 Token / TTS / STT 三个环节。
    用法: cd backend && python -m core.baidu_speech
    """
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

    app_key = os.getenv("BAIDU_APP_KEY", "")
    secret_key = os.getenv("BAIDU_SECRET_KEY", "")
    if not app_key or not secret_key:
        print("❌ 请在 .env 中配置 BAIDU_APP_KEY 和 BAIDU_SECRET_KEY")
        return

    client = BaiduSpeechClient(app_key=app_key, secret_key=secret_key)

    # ── 1. 测试 Token ──
    print("\n" + "=" * 50)
    print("  测试 1/3: 获取 access_token")
    print("=" * 50)
    try:
        token = client.access_token
        print(f"  ✅ Token: {token[:20]}...{token[-10:]}")
    except Exception as e:
        print(f"  ❌ Token 获取失败: {e}")
        return

    # ── 2. 测试 TTS ──
    print("\n" + "=" * 50)
    print("  测试 2/3: 文本转语音 (TTS)")
    print("=" * 50)
    test_text = "你好，我是ProView面试官，很高兴认识你。"
    try:
        pcm_data = client.text_to_speech(test_text, per=4115, spd=5, vol=8, aue=4)
        print(f"  ✅ TTS 成功! PCM 大小: {len(pcm_data)} bytes")

        # 尝试播放
        try:
            import pyaudio
            pa = pyaudio.PyAudio()
            stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
            print("  🔊 正在播放...")
            for i in range(0, len(pcm_data), 4096):
                stream.write(pcm_data[i:i + 4096])
            stream.stop_stream()
            stream.close()
            pa.terminate()
            print("  🔊 播放完毕")
        except ImportError:
            print("  ⚠️ 未安装 pyaudio，跳过播放（pip install pyaudio）")
    except Exception as e:
        print(f"  ❌ TTS 失败: {e}")
        pcm_data = None

    # ── 3. 测试 STT（用 TTS 生成的音频反向识别） ──
    print("\n" + "=" * 50)
    print("  测试 3/3: 语音转文本 (STT)")
    print("=" * 50)
    if pcm_data:
        print(f"  📤 用 TTS 生成的 PCM 做 STT 回环测试...")
        try:
            result = client.speech_to_text(pcm_data, fmt="pcm", rate=16000)
            print(f"  ✅ STT 识别结果: {result}")
            print(f"  📝 原始文本:     {test_text}")
        except Exception as e:
            print(f"  ❌ STT 失败: {e}")
    else:
        print("  ⚠️ 无 TTS 音频数据，跳过 STT 测试")

    print("\n" + "=" * 50)
    print("  测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    test_api()
