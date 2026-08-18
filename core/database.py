import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DEFAULT_DATABASE_URL = "sqlite:///./ai_media_factory.db"
DATABASE_URL = os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
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
from core.models.execution_log_orm import ExecutionLogORM
