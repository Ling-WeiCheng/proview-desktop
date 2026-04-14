"""Structured content loader for career planning documents."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_paths import get_resource_path


@dataclass(frozen=True)
class CareerPlanningDocumentRepository:
    source_path: Path = get_resource_path("data", "career_planning_docs.json")

    def _load_raw(self) -> Dict[str, Any]:
        with self.source_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def list_documents(self) -> List[Dict[str, Any]]:
        payload = self._load_raw()
        return list(payload.get("documents", []))

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        for document in self.list_documents():
            if document.get("id") == document_id:
                return document
        return None

    def get_catalog(self) -> Dict[str, Any]:
        payload = self._load_raw()
        return {
            "version": payload.get("version", "1.0.0"),
            "updated_at": payload.get("updated_at"),
            "documents": payload.get("documents", []),
        }
