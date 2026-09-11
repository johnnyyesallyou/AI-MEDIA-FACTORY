"""
Sprint 66.5: Database Migration - Create pipeline_failures table
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.dirname(__file__))

from core.database import Base, engine
from core.models.pipeline_failure_orm import PipelineFailure

def create_tables():
    """Create all tables in the database"""
    print("Creating pipeline_failures table...")
    
    # Create only PipelineFailure table (in case others already exist)
    PipelineFailure.__table__.create(engine, checkfirst=True)
    
    print("✅ pipeline_failures table created successfully")

if __name__ == "__main__":
    try:
        create_tables()
        print("✅ Migration completed")
    except Exception as e:
        print(f"❌ Error: {e}")
# Sprint 73.3 migration moved to migrations/002_add_llm_metrics.py

        sys.exit(1)

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from core.database import engine, SessionLocal

COLUMNS = {
    "llm_calls": "INTEGER DEFAULT 0",
    "llm_errors": "INTEGER DEFAULT 0",
    "llm_latency_ms": "INTEGER DEFAULT 0",
    "tokens_in": "INTEGER DEFAULT 0",
    "tokens_out": "INTEGER DEFAULT 0",
    "llm_model": "VARCHAR",
}


def add_llm_columns() -> None:
    db = SessionLocal()
    try:
        is_postgres = db.bind.dialect.name == "postgresql"
        existing = {
            row[0] for row in db.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'pipeline_run_metrics'"
            ))
        }
        if not existing:
            print("⚠️  table pipeline_run_metrics not found — skipping (created by ORM)")
            return
        for name, ddl in COLUMNS.items():
            if name in existing:
                print(f"   ↩ column {name} already exists — skip")
                continue
            db.execute(text(f"ALTER TABLE pipeline_run_metrics ADD COLUMN {name} {ddl}"))
            print(f"   ✅ added column {name} ({ddl})")
        db.commit()
        print("✅ Migration completed")
    finally:
        db.close()


if __name__ == "__main__":
    try:
        add_llm_columns()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
