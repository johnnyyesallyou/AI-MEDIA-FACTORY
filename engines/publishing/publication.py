"""Normalized publication object - Sprint 25.2.

Publisher получает готовый объект и занимается ТОЛЬКО доставкой.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PublicationButton:
    text: str
    url: str


@dataclass
class Publication:
    """Нормализованный объект публикации для любой платформы."""
    text: str
    image_url: Optional[str] = None
    buttons: List[PublicationButton] = field(default_factory=list)
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)