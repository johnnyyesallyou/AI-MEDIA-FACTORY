import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from core.models.channel_orm import ChannelORM


class ChannelRepository:
    """Инкапсулирует доступ к таблице channels. Роуты не знают про SQLAlchemy напрямую."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, **fields) -> ChannelORM:
        channel = ChannelORM(id=str(uuid.uuid4()), sources=[], **fields)
        self.db.add(channel)
        self.db.commit()
        self.db.refresh(channel)
        return channel

    def get(self, channel_id: str) -> Optional[ChannelORM]:
        return self.db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()

    def list_all(self) -> List[ChannelORM]:
        return self.db.query(ChannelORM).order_by(ChannelORM.created_at.desc()).all()

    def update(self, channel_id: str, **fields) -> Optional[ChannelORM]:
        channel = self.get(channel_id)
        if not channel:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(channel, key, value)
        channel.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(channel)
        return channel


    def remove_source(self, channel_id: str, source_id: str) -> Optional[ChannelORM]:
        """Удаляет источник по ID из JSON-массива sources канала."""
        channel = self.get(channel_id)
        if not channel:
            return None
        current = channel.sources or []
        new_sources = [s for s in current if s.get("id") != source_id]
        if len(new_sources) == len(current):
            return channel  # не нашли
        channel.sources = new_sources
        channel.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(channel)
        return channel

    def delete(self, channel_id: str) -> bool:
        channel = self.get(channel_id)
        if not channel:
            return False
        self.db.delete(channel)
        self.db.commit()
        return True

    def connect_telegram(self, channel_id: str, bot_token: str, chat_id: str) -> Optional[ChannelORM]:
        return self.update(channel_id, bot_token=bot_token, chat_id=chat_id, is_connected=True)

    def add_source(self, channel_id: str, source: dict) -> Optional[ChannelORM]:
        channel = self.get(channel_id)
        if not channel:
            return None
        sources = list(channel.sources or [])
        sources.append(source)
        channel.sources = sources
        channel.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(channel)
        return channel

    def delete_cascade(self, channel_id: str) -> bool:
        """Schema-driven cascade delete: удаляет строки из ВСЕХ таблиц,
        имеющих FK на channels, затем сам канал."""
        from sqlalchemy import text
        try:
            channel = self.db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
            if not channel:
                return False

            if self.db.get_bind().dialect.name == "postgresql":
                rows = self.db.execute(text("""
                    SELECT DISTINCT child.relname AS tbl, a.attname AS col
                    FROM pg_constraint c
                    JOIN pg_class parent ON parent.oid = c.confrelid
                    JOIN pg_class child ON child.oid = c.conrelid
                    JOIN unnest(c.conkey) WITH ORDINALITY AS k(attnum, ord) ON TRUE
                    JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum
                    WHERE parent.relname = 'channels' AND c.contype = 'f'
                """)).fetchall()
                for tbl, col in rows:
                    self.db.execute(
                        text('DELETE FROM "' + tbl + '" WHERE "' + col + '" = :cid'),
                        {"cid": channel_id},
                    )
            else:
                from core.models.channel_schedule_orm import ChannelScheduleORM
                self.db.query(ChannelScheduleORM).filter(
                    ChannelScheduleORM.channel_id == channel_id
                ).delete()

            self.db.delete(channel)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            import traceback
            traceback.print_exc()
            return False
