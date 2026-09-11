"""
Sprint 75.1.x: Migration - recreate channel_profiles in Sprint 67.2 schema.

Реальная БД (SQLite ai_media_factory.db) содержит СТАРУЮ Sprint 8.2 схему
(platform/audience/tone/format/emoji_usage/length_chars/...), несовместимую
с ChannelProfileORM (Sprint 67.2: archetype/theme/niche/content/research/...).
Из-за этого Priority 1 в backend/automation/profile_config.py был мёртв.

Подтверждено перед миграцией: таблица пуста (0 строк), 0 каналов привязано
к профилям -> безопасно пересоздать таблицу без переноса данных.
Защита: если в старой таблице появились строки — legacy данные сохраняются
в channel_profiles_legacy_82 для ручного разбора.

Идемпотентно: повторный запуск — no-op.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # project root (core/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import text
from core.database import SessionLocal, Base
from core.models.channel_profile_orm import ChannelProfileORM

TABLE = "channel_profiles"
LEGACY_TABLE = "channel_profiles_legacy_82"


def _existing_columns(db) -> set:
    rows = db.execute(text(f"PRAGMA table_info({TABLE})"))
    return {row[1] for row in rows}


def recreate_channel_profiles() -> None:
    db = SessionLocal()
    try:
        # Идемпотентность: таблица уже в новой схеме?
        cols = _existing_columns(db)
        if not cols:
            print(f"table {TABLE} not found -> creating via ORM")
            Base.metadata.create_all(bind=db.bind, tables=[ChannelProfileORM.__table__])
            db.commit()
            print("OK: table created (Sprint 67.2 schema)")
            return

        if "archetype" in cols:
            print(f"OK: {TABLE} already in Sprint 67.2 schema (archetype present) — nothing to do")
            return

        # Старая Sprint 8.2 схема -> пересоздание с защитой данных
        legacy_count = db.execute(text(f"SELECT COUNT(*) FROM {TABLE}")).scalar()
        print(f"old Sprint 8.2 schema detected (no archetype). Rows: {legacy_count}")

        if legacy_count > 0:
            db.execute(text(f"ALTER TABLE {TABLE} RENAME TO {LEGACY_TABLE}"))
            db.commit()
            print(f"WARNING: legacy data preserved in {LEGACY_TABLE} — review manually!")
        else:
            print("table is empty -> safe to drop and recreate")

        db.execute(text(f"DROP TABLE {TABLE}"))
        db.commit()
        Base.metadata.create_all(bind=db.bind, tables=[ChannelProfileORM.__table__])
        db.commit()
        print("OK: table recreated (Sprint 67.2 schema)")
    finally:
        db.close()


if __name__ == "__main__":
    try:
        recreate_channel_profiles()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
