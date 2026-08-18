from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4

class Article(BaseModel):
    """Единая модель статьи для Research Domain."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    summary: str = ""
    content: str = ""
    url: str
    source: str
    source_type: str = "rss"
    published_at: Optional[datetime] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    language: str = "en"
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    trust_score: float = 0.0
    duplicate_score: float = 0.0
    importance_score: float = 0.0
    embeddings: Optional[List[float]] = None
    status: str = "raw"
    metadata: dict = Field(default_factory=dict)

    def to_dict(self) -> dict:
        return self.model_dump()

    def __str__(self) -> str:
        return f"Article(title='{self.title[:50]}...', source='{self.source}', score={self.importance_score:.1f})"
