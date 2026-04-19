#!/usr/bin/env python3
"""Ingest a PR comment event and persist a memory into a local SQLite DB.

This script is intended to be run from a GitHub Actions workflow triggered by
`issue_comment` events. It expects the environment variable `GITHUB_EVENT_PATH`
to point to the event payload JSON file.

Behavior:
- read the comment payload
- verify it's a PR comment and contains 'Copilot' (case-insensitive)
- initialize `data/memories.db` (SQLite) and insert a memory record
- do a simple fuzzy deduplication using rapidfuzz before inserting

Note: This is an MVP storage suitable for low write volume. For production,
consider Supabase/Neon or a dedicated vector DB when embeddings are needed.
"""

import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime
from pathlib import Path

try:
    from rapidfuzz import fuzz, process
except Exception:
    print("Missing dependency 'rapidfuzz'. Install it in your environment.")
    raise


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "memories.db"


def get_event():
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        print("GITHUB_EVENT_PATH not set", file=sys.stderr)
        sys.exit(2)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def init_db(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS memories (
      id TEXT PRIMARY KEY,
      repo TEXT NOT NULL,
      pr_number INTEGER NOT NULL,
      comment_text TEXT NOT NULL,
      author TEXT,
      created_at TEXT,
      tags TEXT
    );
    """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_repo_pr ON memories(repo, pr_number);")
    conn.commit()


def load_all_texts(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, comment_text FROM memories")
    return cur.fetchall()


def add_memory(conn, repo, pr_number, comment_text, author, tags=None):
    cur = conn.cursor()
    mem_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"
    tags_str = ",".join(tags or [])
    cur.execute(
        "INSERT INTO memories(id,repo,pr_number,comment_text,author,created_at,tags) VALUES (?,?,?,?,?,?,?)",
        (mem_id, repo, pr_number, comment_text, author, created_at, tags_str),
    )
    conn.commit()
    return mem_id


def find_similar_texts(choices, query, limit=5):
    # choices is list of tuples (id, text)
    mapping = {str(i): t for i, (i_id, t) in enumerate(choices)}
    # rapidfuzz.process.extract expects mapping from key->text
    results = process.extract(query, mapping, scorer=fuzz.token_sort_ratio, limit=limit)
    out = []
    for text, score, key in results:
        out.append((int(key), score))
    return out


def main():
    ev = get_event()

    # ensure it's a PR comment
    issue = ev.get("issue") or {}
    if not issue.get("pull_request"):
        print("Not a pull request comment; exiting.")
        return

    comment = ev.get("comment", {}).get("body", "")
    if not comment or "copilot" not in comment.lower():
        print("Comment does not contain 'Copilot' term; exiting.")
        return

    repo_full = ev.get("repository", {}).get("full_name")
    pr_number = issue.get("number")
    author = ev.get("comment", {}).get("user", {}).get("login")

    # minimal length guard
    if len(comment.strip()) < 10:
        print("Comment too short; ignoring.")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=30, check_same_thread=False)
    try:
        init_db(conn)

        # deduplicate: if an existing comment is very similar (score >= 90) skip
        rows = load_all_texts(conn)
        if rows:
            results = find_similar_texts(rows, comment, limit=5)
            for idx, score in results:
                # idx is index into rows list
                existing_id, existing_text = rows[idx]
                if score >= 90:
                    print(f"Found near-duplicate memory (score={score}) id={existing_id}; skipping insert")
                    return

        mem_id = add_memory(conn, repo_full, pr_number, comment, author, tags=["pr_comment"])
        print(f"Inserted memory id={mem_id}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
