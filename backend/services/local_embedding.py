from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import List, Sequence

try:
    import numpy as np
except Exception:
    np = None

try:
    import onnxruntime as ort
except Exception:
    ort = None

try:
    from tokenizers import Tokenizer
except Exception:
    Tokenizer = None


class LocalEmbeddingService:
    _instances: dict[tuple[str, int], "LocalEmbeddingService"] = {}
    _lock = Lock()

    def __new__(cls, model_dir: str, max_length: int = 256):
        key = (str(Path(model_dir).resolve()), int(max_length))
        with cls._lock:
            instance = cls._instances.get(key)
            if instance is None:
                instance = super().__new__(cls)
                cls._instances[key] = instance
        return instance

    def __init__(self, model_dir: str, max_length: int = 256):
        if getattr(self, "_initialized", False):
            return
        self.model_dir = Path(model_dir).resolve()
        self.max_length = int(max_length)
        self._tokenizer = None
        self._session = None
        self._initialized = True

    @staticmethod
    def dependencies_available() -> bool:
        return np is not None and ort is not None and Tokenizer is not None

    def is_available(self) -> bool:
        return (
            self.dependencies_available()
            and (self.model_dir / "tokenizer.json").exists()
            and (self.model_dir / "model.onnx").exists()
        )

    def _ensure_runtime(self) -> None:
        if not self.dependencies_available():
            raise RuntimeError("numpy, onnxruntime and tokenizers are required for local embeddings.")
        if not self.is_available():
            raise RuntimeError(f"Local embedding model not found under: {self.model_dir}")

        if self._tokenizer is None:
            self._tokenizer = Tokenizer.from_file(str(self.model_dir / "tokenizer.json"))
            self._tokenizer.enable_truncation(max_length=self.max_length)
            self._tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=self.max_length)

        if self._session is None:
            self._session = ort.InferenceSession(
                str(self.model_dir / "model.onnx"),
                providers=["CPUExecutionProvider"],
            )

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        if not texts:
            return []

        self._ensure_runtime()
        assert self._tokenizer is not None
        assert self._session is not None
        assert np is not None

        input_names = {item.name for item in self._session.get_inputs()}
        encodings = self._tokenizer.encode_batch(list(texts))

        input_ids = np.asarray([encoding.ids for encoding in encodings], dtype=np.int64)
        attention_mask = np.asarray([encoding.attention_mask for encoding in encodings], dtype=np.int64)

        feed = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }
        if "token_type_ids" in input_names:
            token_type_ids = [
                encoding.type_ids if encoding.type_ids else [0] * len(encoding.ids)
                for encoding in encodings
            ]
            feed["token_type_ids"] = np.asarray(token_type_ids, dtype=np.int64)

        outputs = self._session.run(None, feed)
        token_embeddings = outputs[0]
        mask_expanded = attention_mask[..., None].astype(np.float32)
        summed = (token_embeddings * mask_expanded).sum(axis=1)
        counts = np.clip(mask_expanded.sum(axis=1), 1e-9, None)
        sentence_embeddings = summed / counts
        norms = np.linalg.norm(sentence_embeddings, axis=1, keepdims=True)
        sentence_embeddings = sentence_embeddings / np.clip(norms, 1e-12, None)
        return [vector.astype(np.float32).tolist() for vector in sentence_embeddings]

    def embed_text(self, text: str) -> List[float]:
        vectors = self.embed_texts([text])
        return vectors[0] if vectors else []
