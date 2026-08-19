"""
Data models для WritingEngine v2.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime


class ContentBrief(BaseModel):
    """Бриф для генерации контента."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    topic: str
    audience: str
    goal: str
    tone: str
    length_chars: int
    call_to_action: str
    source_url: Optional[str] = None
    source_text: Optional[str] = None
    key_facts: List[str] = Field(default_factory=list)
    forbidden_words: List[str] = Field(default_factory=lambda: ["спам", "кликбейт", "шок"])
    platform: str = Field(default="telegram")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationIssue(BaseModel):
    """Проблема, найденная валидатором."""
    category: str  # "grammar" | "style" | "fact"
    severity: str  # "error" | "warning" | "info"
    message: str
    suggestion: str


class ContentDraft(BaseModel):
    """Сгенерированный черновик контента."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    brief_id: str
    title: str
    body: str
    hashtags: List[str] = Field(default_factory=list)
    estimated_read_time: int = Field(default=0)
    quality_score: float = Field(default=0.0)
    model_used: str = Field(default="")
    tokens_input: int = Field(default=0)
    tokens_output: int = Field(default=0)
    platform: str = Field(default="telegram")
    validation_issues: List[ValidationIssue] = Field(default_factory=list)
    fact_check_passed: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)