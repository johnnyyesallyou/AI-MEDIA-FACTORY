"""Sprint 65: Smart Channel Intelligence — data models.

ChannelIntent: что пользователь хочет создать (domain/topic/audience)
ChannelStrategy: как это реализовать (profile/sources/formatter)
CapabilityDefinition: возможности source/formatter/media
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ChannelIntent:
    """Что пользователь хочет создать."""
    raw_description: str
    
    domain: str                              # "automotive", "technology", "science"
    topic: str                               # "car_news", "ai_news", "biology"
    subtopics: List[str] = field(default_factory=list)  # ["new_models", "electric_cars"]
    
    content_goal: str = "information"        # "information", "entertainment", "education"
    audience: str = "general"                # "car_enthusiasts", "developers", "students"
    language: str = "ru"
    geography: Optional[str] = None          # "russia", "global"
    
    content_frequency: str = "daily"         # "hourly", "daily", "weekly"
    suggested_content_types: List[str] = field(default_factory=list)
    
    confidence: float = 0.0                  # 0.0-1.0 from classifier
    reasoning: str = ""


@dataclass
class ChannelStrategy:
    """Как реализовать канал."""
    profile_key: str                         # "automotive_news", "ai_news"
    
    research_strategy: str = "rss_news"      # "rss_news", "manga_updates", "anime_episodes"
    sources: List[str] = field(default_factory=list)  # ["motor1", "autocar"]
    
    formatter: str = "news_formatter"        # "news_formatter", "manga_formatter"
    media_policy: str = "source_image"       # "source_image", "pixabay_search", "none"
    
    publishing_frequency: str = "6h"         # "30m", "1h", "6h", "daily"
    publishing_mode: str = "approval_required"  # "auto", "approval_required", "manual"
    
    reasoning: List[str] = field(default_factory=list)


@dataclass
class CapabilityDefinition:
    """Возможности компонента (source/formatter/media)."""
    id: str
    name: str
    component_type: str                      # "source", "formatter", "media_policy"
    
    # Что поддерживает
    supported_domains: List[str] = field(default_factory=list)
    supported_topics: List[str] = field(default_factory=list)
    supported_content_types: List[str] = field(default_factory=list)
    
    # Capabilities (что умеет)
    capabilities: List[str] = field(default_factory=list)
    # Примеры: ["news", "images", "reviews", "video", "long_form"]
    
    # Metadata
    language: str = "any"                    # "ru", "en", "any"
    reliability: float = 1.0                 # 0.0-1.0 (для source scoring)
    
    def supports_intent(self, intent: ChannelIntent) -> bool:
        """Проверяет совместимость с intent."""
        # Domain match
        if self.supported_domains and intent.domain not in self.supported_domains:
            if "general" not in self.supported_domains:
                return False
        
        # Topic match (если указаны topics)
        if self.supported_topics:
            topic_match = (
                intent.topic in self.supported_topics
                or any(st in self.supported_topics for st in intent.subtopics)
                or "general" in self.supported_topics
            )
            if not topic_match:
                return False
        
        # Content type match
        if self.supported_content_types:
            if not any(ct in self.supported_content_types for ct in intent.suggested_content_types):
                if intent.content_goal not in self.supported_content_types:
                    return False
        
        return True