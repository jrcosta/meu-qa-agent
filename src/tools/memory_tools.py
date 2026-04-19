"""Tools for reading and writing memories from data/memories.db (SQLite)."""

import sqlite3
from pathlib import Path
from typing import List, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from rapidfuzz import fuzz, process

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DB_PATH = DATA_DIR / "memories.db"


def _get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            repo TEXT NOT NULL,
            pr_number INTEGER NOT NULL,
            lesson TEXT NOT NULL,
            original_comment TEXT,
            author TEXT,
            created_at TEXT,
            tags TEXT
        );
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_repo ON memories(repo);")
    conn.commit()


def fetch_all_lessons(conn: sqlite3.Connection) -> list[dict]:
    cur = conn.cursor()
    cur.execute("SELECT id, repo, pr_number, lesson, author, created_at, tags FROM memories ORDER BY created_at DESC")
    rows = cur.fetchall()
    return [
        {"id": r[0], "repo": r[1], "pr_number": r[2], "lesson": r[3], "author": r[4], "created_at": r[5], "tags": r[6]}
        for r in rows
    ]


# ---------------------------------------------------------------------------
# CrewAI Tool: query memories
# ---------------------------------------------------------------------------

class QueryMemoriesInput(BaseModel):
    query: str = Field(..., description="Texto de busca para encontrar memórias/lições relevantes.")
    limit: int = Field(10, description="Quantidade máxima de memórias retornadas.")


class QueryMemoriesTool(BaseTool):
    name: str = "query_memories"
    description: str = (
        "Consulta o banco de memórias (lições aprendidas) para evitar erros já cometidos. "
        "Retorna lições relevantes ordenadas por similaridade com a busca."
    )
    args_schema: Type[BaseModel] = QueryMemoriesInput

    def _run(self, query: str, limit: int = 10) -> str:
        if not DB_PATH.exists():
            return "Nenhuma memória disponível ainda (banco não existe)."

        conn = _get_conn()
        try:
            init_db(conn)
            all_memories = fetch_all_lessons(conn)
        finally:
            conn.close()

        if not all_memories:
            return "Nenhuma memória registrada ainda."

        choices = {str(i): m["lesson"] for i, m in enumerate(all_memories)}
        results = process.extract(query, choices, scorer=fuzz.token_sort_ratio, limit=limit)

        output_lines: list[str] = []
        for text, score, key in results:
            if score < 40:
                continue
            mem = all_memories[int(key)]
            output_lines.append(
                f"[score={score}] (PR #{mem['pr_number']} em {mem['repo']}, por {mem['author']})\n"
                f"  Lição: {mem['lesson']}"
            )

        if not output_lines:
            return "Nenhuma memória relevante encontrada para esta consulta."

        return "\n\n".join(output_lines)


class ListAllMemoriesInput(BaseModel):
    limit: int = Field(20, description="Quantidade máxima de memórias.")


class ListAllMemoriesTool(BaseTool):
    name: str = "list_all_memories"
    description: str = "Lista todas as memórias/lições aprendidas armazenadas, ordenadas por data decrescente."
    args_schema: Type[BaseModel] = ListAllMemoriesInput

    def _run(self, limit: int = 20) -> str:
        if not DB_PATH.exists():
            return "Nenhuma memória disponível ainda (banco não existe)."

        conn = _get_conn()
        try:
            init_db(conn)
            all_memories = fetch_all_lessons(conn)
        finally:
            conn.close()

        if not all_memories:
            return "Nenhuma memória registrada ainda."

        lines: list[str] = []
        for mem in all_memories[:limit]:
            lines.append(
                f"- [{mem['created_at']}] PR #{mem['pr_number']} ({mem['repo']}): {mem['lesson']}"
            )

        return "\n".join(lines)
