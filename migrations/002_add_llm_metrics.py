"""
Sprint 73.3: Migration - add LLM metrics columns to pipeline_run_metrics.

Добавляет: llm_calls, llm_errors, llm_latency_ms, tokens_in, tokens_out, llm_model.
Идемпотентно: колонки добавляются только если отсутствуют.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # project root (core/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import text
from core.database import SessionLocal

COLUMNS = {
    "llm_calls": "INTEGER DEFAULT 0",
    "llm_errors": "INTEGER DEFAULT 0",
    "llm_latency_ms": "INTEGER DEFAULT 0",
    "tokens_in": "INTEGER DEFAULT 0",
    "tokens_out": "INTEGER DEFAULT 0",
    "llm_model": "VARCHAR",
}


def _existing_columns(db, dialect: str) -> set:
    if dialect == "sqlite":
        rows = db.execute(text("PRAGMA table_info(pipeline_run_metrics)"))
        return {row[1] for row in rows}
    return {
        row[0] for row in db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'pipeline_run_metrics'"
        ))
    }


def add_llm_columns() -> None:
    db = SessionLocal()
    try:
        dialect = db.bind.dialect.name
        existing = _existing_columns(db, dialect)
        if not existing:
            print("table pipeline_run_metrics not found — skipping (created by ORM)")
            return
        for name, ddl in COLUMNS.items():
            if name in existing:
                print(f"   skip {name} (already exists)")
                continue
            db.execute(text(f"ALTER TABLE pipeline_run_metrics ADD COLUMN {name} {ddl}"))
            print(f"   added {name} ({ddl})")
        db.commit()
        print("OK: migration completed")
    finally:
        db.close()


if __name__ == "__main__":
    try:
        add_llm_columns()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)