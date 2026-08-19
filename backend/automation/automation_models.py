from typing import List, Optional
from pydantic import BaseModel, Field


class AutomationSettings(BaseModel):
    enabled: bool = True
    research_interval: str = Field(default="60m")
    publish_times: List[str] = Field(default=["09:00", "13:00", "18:00"])
    timezone: str = Field(default="Europe/Moscow")
    auto_publish: bool = False
    human_review: bool = True
    max_posts_per_day: int = Field(default=5, ge=1, le=20)
    breaking_news: bool = True


class AutomationRunResult(BaseModel):
    status: str
    details: Optional[str] = None
