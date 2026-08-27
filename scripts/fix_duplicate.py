import pathlib

# Читаем post_history_orm.py
p = pathlib.Path("/app/core/models/post_history_orm.py")
c = p.read_text(encoding="utf-8")

# Удаляем PostMetricsORM (дубликат)
# Оставляем только PostHistoryORM и ChannelLearningsORM

new_content = '''"""Post History ORM - Sprint 57.

Отслеживание истории постов + learnings.
Примечание: PostMetrics уже существует в core.models.analytics
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base


class PostHistoryORM(Base):
    __tablename__ = "post_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = Column(String, ForeignKey("channels.id"), nullable=False, index=True)
    content_id = Column(String, ForeignKey("content.id"), nullable=True)
    platform = Column(String(50))
    
    text = Column(Text)
    image_url = Column(String(2000))
    video_url = Column(String(2000))
    media_type = Column(String(50))  # 'image', 'video', 'none'
    
    message_id = Column(String(200))  # ID поста на платформе
    posted_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Используем существующую PostMetric из core.models.analytics
    # metrics = relationship("PostMetricsORM", back_populates="post", cascade="all, delete-orphan")


class ChannelLearningsORM(Base):
    __tablename__ = "channel_learnings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = Column(String, ForeignKey("channels.id"), nullable=False, index=True)
    
    pattern = Column(String(500))  # e.g., "video_increases_views_by_50%"
    score = Column(Float)  # 0.0 - 1.0
    evidence_count = Column(Integer, default=1)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    metadata_json = Column(Text)  # JSON string с деталями
'''

p.write_text(new_content, encoding="utf-8")
print("[OK] Удалён PostMetricsORM из post_history_orm.py")

# Обновляем __init__.py - убираем PostMetricsORM из импорта
init_p = pathlib.Path("/app/core/models/__init__.py")
init_c = init_p.read_text(encoding="utf-8")

init_c = init_c.replace(
    "from core.models.post_history_orm import PostHistoryORM, PostMetricsORM, ChannelLearningsORM  # Sprint 57",
    "from core.models.post_history_orm import PostHistoryORM, ChannelLearningsORM  # Sprint 57\nfrom core.models.analytics import PostMetric  # Sprint 57 (existing)",
)

init_c = init_c.replace(
    '    "PostMetricsORM",\n',
    '    "PostMetric",  # из analytics.py\n',
)

init_p.write_text(init_c, encoding="utf-8")
print("[OK] Обновлён core/models/__init__.py")