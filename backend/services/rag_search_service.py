from __future__ import annotations

import re
from typing import Dict, List, Optional

from sqlalchemy import create_engine, text

from direct_store import normalize_db_url
from services.local_embedding import LocalEmbeddingService


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _slugify_key(text_value: str) -> str:
    value = _normalize_text(text_value).lower()
    value = value.replace("/", "-").replace("\\", "-")
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-_")
    return value or "all"


def _vector_literal(vector: Optional[List[float]]) -> Optional[str]:
    if not vector:
        return None
    return "[" + ",".join(f"{value:.8f}" for value in vector) + "]"


class RAGSearchService:
    def __init__(self, db_url: str, local_model_dir: str = "", local_max_length: int = 256):
        self.db_url = normalize_db_url(db_url)
        self.engine = create_engine(self.db_url, pool_pre_ping=True, pool_recycle=300)
        self._embedder = None
        if local_model_dir:
            embedder = LocalEmbeddingService(local_model_dir, local_max_length)
            self._embedder = embedder if embedder.is_available() else None

    def _embed_query_literal(self, query: str) -> Optional[str]:
        if not self._embedder or not _normalize_text(query):
            return None
        try:
            return _vector_literal(self._embedder.embed_text(query))
        except Exception as exc:
            print(f"[RAGSearchService] local embedding failed: {exc}")
            return None

    def _fetch_rows(self, sql_text: str, params: Dict) -> List[Dict]:
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_text), params)
            return [dict(row) for row in result.mappings().all()]

    @staticmethod
    def _metadata(row: Dict, *keys: str) -> Dict:
        metadata = row.get("metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}
        for key in keys:
            value = row.get(key)
            if value is not None and key not in metadata:
                metadata[key] = value
        return metadata

    def search_job_descriptions(
        self,
        query: str,
        top_k: int = 3,
        difficulty: str = None,
        interview_type: str = None,
    ) -> List[Dict]:
        query_text = _normalize_text(query)
        job_key = _slugify_key(query_text) if query_text else ""
        query_like = f"%{query_text}%" if query_text else "%"
        embedding = self._embed_query_literal(query_text)
        semantic_score = "0.0"
        if embedding:
            semantic_score = "greatest(0, 1 - (embedding <=> cast(:embedding as vector)))"

        sql_text = f"""
            select
                external_id,
                canonical_job_title,
                content,
                metadata,
                tech_tags,
                domain_tags,
                must_have_skills,
                priority,
                (
                    case
                        when :job_key <> '' and lower(job_key) = lower(:job_key) then 2
                        when canonical_job_title ilike :query_like then 1
                        else 0
                    end
                ) as title_rank,
                (
                    case
                        when content ilike :query_like then 1
                        else 0
                    end
                ) as lexical_rank,
                {semantic_score} as semantic_rank
            from rag.job_profiles
            where is_active = true
              and (
                :difficulty = ''
                or :difficulty = any(difficulty_tags)
                or 'all' = any(difficulty_tags)
              )
              and (
                :interview_type = ''
                or :interview_type = any(interview_types)
                or 'all' = any(interview_types)
              )
            order by
                title_rank desc,
                lexical_rank desc,
                semantic_rank desc,
                priority desc
            limit :top_k
        """
        params = {
            "job_key": job_key,
            "query_like": query_like,
            "difficulty": _normalize_text(difficulty).lower(),
            "interview_type": _normalize_text(interview_type).lower(),
            "top_k": max(1, int(top_k)),
        }
        if embedding:
            params["embedding"] = embedding

        rows = self._fetch_rows(sql_text, params)
        return [
            {
                "id": row.get("external_id"),
                "document": row.get("content") or "",
                "content": row.get("content") or "",
                "metadata": self._metadata(
                    row,
                    "canonical_job_title",
                    "tech_tags",
                    "domain_tags",
                    "must_have_skills",
                ) | {
                    "job_name": row.get("canonical_job_title") or "",
                    "tags": ", ".join(row.get("tech_tags") or []),
                },
            }
            for row in rows
        ]

    def search_questions(
        self,
        query: str,
        job_filter: str = None,
        top_k: int = 5,
        difficulty: str = None,
        interview_type: str = None,
        style: str = None,
        stage: str = None,
    ) -> List[Dict]:
        job_title = _normalize_text(job_filter)
        job_key = _slugify_key(job_title) if job_title else ""
        query_text = _normalize_text(query) or job_title
        query_like = f"%{query_text}%" if query_text else "%"
        embedding = self._embed_query_literal(query_text)
        semantic_score = "0.0"
        if embedding:
            semantic_score = "greatest(0, 1 - (embedding <=> cast(:embedding as vector)))"

        sql_text = f"""
            select
                external_id,
                canonical_job_title,
                question_text,
                followup_guide,
                rubric_5,
                rubric_3,
                rubric_1,
                dimension,
                stage,
                metadata,
                priority,
                (
                    case
                        when :job_key <> '' and lower(job_key) = lower(:job_key) then 2
                        when upper(canonical_job_title) = 'ALL' then 1
                        else 0
                    end
                ) as job_rank,
                (
                    case
                        when :difficulty = '' then 1
                        when :difficulty = any(difficulty_tags) or 'all' = any(difficulty_tags) then 1
                        else 0
                    end
                ) as difficulty_rank,
                (
                    case
                        when :interview_type = '' then 1
                        when :interview_type = any(interview_types) or 'all' = any(interview_types) then 1
                        else 0
                    end
                ) as interview_rank,
                (
                    case
                        when :style = '' then 1
                        when :style = any(style_tags) or 'all' = any(style_tags) then 1
                        else 0
                    end
                ) as style_rank,
                (
                    case
                        when :stage = '' then 1
                        when lower(stage) = lower(:stage) then 1
                        when lower(stage) = 'core' then 1
                        else 0
                    end
                ) as stage_rank,
                (
                    case
                        when question_text ilike :query_like or followup_guide ilike :query_like then 1
                        else 0
                    end
                ) as lexical_rank,
                {semantic_score} as semantic_rank
            from rag.question_bank
            where is_active = true
              and (
                :job_key = ''
                or lower(job_key) = lower(:job_key)
                or upper(canonical_job_title) = 'ALL'
              )
              and (
                :difficulty = ''
                or :difficulty = any(difficulty_tags)
                or 'all' = any(difficulty_tags)
              )
              and (
                :interview_type = ''
                or :interview_type = any(interview_types)
                or 'all' = any(interview_types)
              )
              and (
                :style = ''
                or :style = any(style_tags)
                or 'all' = any(style_tags)
              )
              and (
                :stage = ''
                or lower(stage) = lower(:stage)
                or lower(stage) = 'core'
              )
            order by
                job_rank desc,
                difficulty_rank desc,
                interview_rank desc,
                style_rank desc,
                stage_rank desc,
                lexical_rank desc,
                semantic_rank desc,
                priority desc
            limit :top_k
        """
        params = {
            "job_key": job_key,
            "difficulty": _normalize_text(difficulty).lower(),
            "interview_type": _normalize_text(interview_type).lower(),
            "style": _normalize_text(style).lower(),
            "stage": _normalize_text(stage).lower(),
            "query_like": query_like,
            "top_k": max(1, int(top_k)),
        }
        if embedding:
            params["embedding"] = embedding

        rows = self._fetch_rows(sql_text, params)
        return [
            {
                "id": row.get("external_id"),
                "document": row.get("question_text") or "",
                "content": row.get("question_text") or "",
                "metadata": self._metadata(
                    row,
                    "canonical_job_title",
                    "dimension",
                    "stage",
                    "rubric_5",
                    "rubric_3",
                    "rubric_1",
                ) | {
                    "score_5": row.get("rubric_5") or "",
                    "score_3": row.get("rubric_3") or "",
                    "score_1": row.get("rubric_1") or "",
                },
            }
            for row in rows
        ]

    def search_hr_scripts(
        self,
        query: str,
        stage: str = None,
        top_k: int = 3,
        interview_type: str = None,
        style: str = None,
    ) -> List[Dict]:
        query_text = _normalize_text(query)
        stage_text = _normalize_text(stage)
        stage_like = f"%{stage_text}%" if stage_text else "%"
        query_like = f"%{query_text}%" if query_text else "%"
        embedding = self._embed_query_literal(query_text)
        semantic_score = "0.0"
        if embedding:
            semantic_score = "greatest(0, 1 - (embedding <=> cast(:embedding as vector)))"

        sql_text = f"""
            select
                external_id,
                stage,
                intent,
                script_text,
                fallback_text,
                metadata,
                priority,
                (
                    case
                        when :stage_text <> '' and stage ilike :stage_like then 2
                        when script_text ilike :query_like then 1
                        else 0
                    end
                ) as stage_rank,
                (
                    case
                        when :interview_type = '' then 1
                        when :interview_type = any(interview_types) or 'all' = any(interview_types) then 1
                        else 0
                    end
                ) as interview_rank,
                (
                    case
                        when :style = '' then 1
                        when :style = any(style_tags) or 'all' = any(style_tags) then 1
                        else 0
                    end
                ) as style_rank,
                {semantic_score} as semantic_rank
            from rag.script_library
            where is_active = true
              and (
                :stage_text = ''
                or stage ilike :stage_like
                or script_text ilike :query_like
              )
              and (
                :interview_type = ''
                or :interview_type = any(interview_types)
                or 'all' = any(interview_types)
              )
              and (
                :style = ''
                or :style = any(style_tags)
                or 'all' = any(style_tags)
              )
            order by
                stage_rank desc,
                interview_rank desc,
                style_rank desc,
                semantic_rank desc,
                priority desc
            limit :top_k
        """
        params = {
            "stage_text": stage_text,
            "stage_like": stage_like,
            "query_like": query_like,
            "interview_type": _normalize_text(interview_type).lower(),
            "style": _normalize_text(style).lower(),
            "top_k": max(1, int(top_k)),
        }
        if embedding:
            params["embedding"] = embedding

        rows = self._fetch_rows(sql_text, params)
        return [
            {
                "id": row.get("external_id"),
                "document": row.get("script_text") or "",
                "content": row.get("script_text") or "",
                "metadata": self._metadata(row, "stage", "intent") | {
                    "fallback_text": row.get("fallback_text") or "",
                },
            }
            for row in rows
        ]
