"""
Sprint 66.4: Database Configuration with Portable JSONB Support

Supports both SQLite (testing) and PostgreSQL (production) with automatic
JSONB type handling through TypeDecorator.
"""

import os
import json
from sqlalchemy import create_engine, text, TypeDecorator, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB

# Environment
DEFAULT_DATABASE_URL = "sqlite:///./ai_media_factory.db"
DATABASE_URL = os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL


class PortableJSONB(TypeDecorator):
    """
    JSONB type that works on both PostgreSQL (native) and SQLite (TEXT).
    
    - PostgreSQL: Uses native JSONB type
    - SQLite: Uses TEXT with JSON serialization/deserialization
    """
    
    impl = Text
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        """Return the appropriate implementation for each database dialect"""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_JSONB())
        else:
            return dialect.type_descriptor(Text())
    
    def process_bind_param(self, value, dialect):
        """Serialize Python value to database format"""
        if dialect.name == 'postgresql':
            # PostgreSQL handles JSONB natively
            return value
        else:
            # SQLite: serialize to JSON string
            if value is not None:
                if isinstance(value, str):
                    return value
                return json.dumps(value, ensure_ascii=False, default=str)
            return None
    
    def process_result_value(self, value, dialect):
        """Deserialize database value to Python format"""
        if dialect.name == 'postgresql':
            # PostgreSQL already returns dict/list
            return value
        else:
            # SQLite: deserialize from JSON string
            if value is not None:
                if isinstance(value, dict) or isinstance(value, list):
                    return value
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return None


# Create engine with proper configuration
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=20,
    max_overflow=30,
    pool_timeout=60,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_sqlite_schema():
    """Reconcile the local SQLite database with the latest channel/workflow schema.
    This keeps the dashboard alive even when a stale db file from a previous schema exists.
    """
    if not DATABASE_URL.startswith("sqlite"):
        return

    try:
        with engine.connect() as conn:
            columns = conn.execute(text("PRAGMA table_info(channels)")).fetchall()
            existing_columns = {row[1] for row in columns}
            if "workflow_id" not in existing_columns:
                conn.execute(text("ALTER TABLE channels ADD COLUMN workflow_id VARCHAR"))
                conn.commit()
    except Exception:
        # The table may not exist yet; the normal `create_all()` boot path will materialize it.
        return


def get_db():
    """FastAPI dependency: одна сессия на запрос, всегда закрывается."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Регистрация новых моделей для автоматического создания таблиц
if os.getenv("APP_ENV") != "test":
    from core.models.execution_log_orm import ExecutionLogORM
