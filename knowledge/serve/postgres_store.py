"""Postgres + pgvector backed store (RDS). Requires PRAXIS_DB_URL."""

from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from knowledge.knowledge_graph.abc import Fact, Insight, State


class PostgresVectorGraph:
    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or os.getenv("PRAXIS_DB_URL")
        if not self.dsn:
            raise RuntimeError("PRAXIS_DB_URL required for PostgresVectorGraph")
        self._ensure_schema()

    def _conn(self) -> Any:
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS facts (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    state TEXT DEFAULT 'proposed',
                    confidence REAL DEFAULT 0.5,
                    provenance TEXT,
                    created_at TIMESTAMPTZ DEFAULT now(),
                    updated_at TIMESTAMPTZ DEFAULT now(),
                    embedding vector(1536)
                );
                """
            )
            conn.commit()

    def write(self, content: str | Insight | Fact, /, **kwargs: Any) -> str:
        fact_id = str(uuid4())
        if isinstance(content, Fact):
            f = content
            fact_id = f.id or fact_id
            title, content_text, prov, conf = f.title, f.content, f.provenance, f.confidence
        elif isinstance(content, Insight):
            title, content_text, prov, conf = content.title, content.content, content.provenance, content.confidence
        else:
            title, content_text, prov, conf = content[:80], content, kwargs.get("provenance", ""), 0.5
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO facts (id,title,content,state,confidence,provenance) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                (fact_id, title, content_text, "proposed", conf, prov),
            )
            conn.commit()
        return fact_id

    def read(self, query: str | None = None, *, state: State | None = None, limit: int = 100) -> list[Fact]:
        sql = "SELECT * FROM facts"
        params: list[Any] = []
        if state:
            sql += " WHERE state = %s"
            params.append(state)
        sql += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [
            Fact(
                id=r["id"],
                title=r["title"] or "",
                content=r["content"] or "",
                state=r["state"],
                confidence=r["confidence"],
                provenance=r["provenance"] or "",
            )
            for r in rows
        ]

    def update_state(self, fact_id: str, new_state: State) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE facts SET state=%s, updated_at=now() WHERE id=%s", (new_state, fact_id))
            conn.commit()

    def list_contradictions(self, fact_id: str) -> list[Fact]:
        return []
