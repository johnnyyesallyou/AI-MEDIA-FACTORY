"""Sprint 67.2: ChannelProfile Pydantic schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class AudienceConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    age: Optional[str] = None
    interests: List[str] = Field(default_factory=list)


class ContentConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    formats: List[str] = Field(default_factory=list)
    max_length: int = 1200


class ResearchConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    freshness_hours: int = 24
    sources: List[str] = Field(default_factory=list)


class MediaConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    preferred: List[str] = Field(default_factory=lambda: ["image"])
    fallback: List[str] = Field(default_factory=list)


class PublishingConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    frequency_per_day: int = 4
    mode: str = "approval_required"


class LearningConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    enabled: bool = True
    min_samples: int = 50


class ChannelProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    archetype: str = "news"
    theme: Optional[str] = None
    niche: Optional[str] = None
    audience: Optional[AudienceConfig] = None
    language: str = "ru"
    tone: str = "informative"
    content: Optional[ContentConfig] = None
    research: Optional[ResearchConfig] = None
    media: Optional[MediaConfig] = None
    publishing: Optional[PublishingConfig] = None
    learning: Optional[LearningConfig] = None


class ChannelProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: Optional[str] = None
    archetype: str
    theme: Optional[str] = None
    niche: Optional[str] = None
    audience: Optional[Dict[str, Any]] = None
    language: str
    tone: str
    content: Optional[Dict[str, Any]] = None
    research: Optional[Dict[str, Any]] = None
    media: Optional[Dict[str, Any]] = None
    publishing: Optional[Dict[str, Any]] = None
    learning: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ChannelProfileListResponse(BaseModel):
    total: int
    profiles: List[ChannelProfileResponse]