"""Sprint 67.2: ChannelProfileORM — persistent channel configuration."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from core.database import Base, PortableJSONB


class ChannelProfileORM(Base):
    """
    Persistent configuration for a channel type/niche.
    
    Связан с ChannelORM через profile_id.
    Определяет archetype, audience, content strategy, research settings, 
    media policy, publishing rules.
    
    Один profile может использоваться многими каналами.
    """
    __tablename__ = "channel_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)
    
    # Classification
    archetype = Column(String(30), nullable=False, default="news", index=True)
    theme = Column(String(50), nullable=True, index=True)      # "technology", "entertainment"
    niche = Column(String(50), nullable=True)                  # "ai", "anime", "manga"
    
    # Audience
    audience = Column(PortableJSONB, nullable=True)            # {"age": "18-45", "interests": [...]}
    
    # Content strategy
    language = Column(String(10), default="ru")
    tone = Column(String(30), default="informative")
    content = Column(PortableJSONB, nullable=True)             # {"formats": [...], "max_length": 1200}
    
    # Research settings
    research = Column(PortableJSONB, nullable=True)            # {"freshness_hours": 24, "sources": [...]}
    
    # Media policy
    media = Column(PortableJSONB, nullable=True)               # {"preferred": ["image"], "fallback": [...]}
    
    # Publishing rules
    publishing = Column(PortableJSONB, nullable=True)          # {"frequency_per_day": 5, "mode": "approval_required"}
    
    # Learning settings
    learning = Column(PortableJSONB, nullable=True)            # {"enabled": true, "min_samples": 50}
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ChannelProfileORM id={self.id[:8]} name={self.name} archetype={self.archetype}>"