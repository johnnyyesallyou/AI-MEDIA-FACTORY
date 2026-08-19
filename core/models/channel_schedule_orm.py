import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey

from core.database import Base


class ChannelScheduleORM(Base):
    """
    Расписание автоматизации канала.
    """

    __tablename__ = "channel_schedules"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    channel_id = Column(
        String,
        ForeignKey("channels.id"),
        nullable=False,
        index=True
    )

    cron_expression = Column(
        String,
        default="0 */3 * * *"
    )

    timezone = Column(
        String,
        default="Europe/Moscow"
    )

    max_posts_per_day = Column(
        Integer,
        default=3
    )

    auto_publish = Column(
        Boolean,
        default=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    last_run = Column(
        DateTime,
        nullable=True
    )

    next_run = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )