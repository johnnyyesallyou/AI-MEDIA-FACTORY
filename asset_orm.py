"""Asset ORM model for storing generated media."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from core.database import Base


class AssetORM(Base):
    """
    Sprint 11: Asset model for storing generated images/videos.
    
    Stores metadata about generated media files (prompts, models, seeds, etc).
    Linked to content via content_id.
    """
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, ForeignKey("content.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False, default="image")  # image/video/audio
    storage_path = Column(String, nullable=False)  # assets/2026/07/uuid.png
    public_url = Column(String, nullable=True)
    prompt = Column(Text, nullable=True)
    model = Column(String, nullable=True)  # flux/sdxl/comfyui
    seed = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    generation_time_ms = Column(Integer, nullable=True)
    status = Column(String, default="generated")  # generating/generated/failed
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AssetORM(id={self.id}, type={self.type}, status={self.status})>"