"""Publication contract for platform-independent media publishing.

Sprint 72.1
Defines the canonical publication object produced by the editorial pipeline
before platform-specific rendering.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MediaAsset:
    """Media attached to a publication."""

    url: str
    media_type: str = "image"
    alt_text: Optional[str] = None


@dataclass
class FormattingOptions:
    """Editorial formatting constraints applied before rendering."""

    max_length: int = 700
    max_paragraphs: int = 4
    emojis: bool = False
    allow_bullets: bool = True


@dataclass
class Publication:
    """Platform-independent publication contract.

    Publication describes what should be published, not how a specific
    platform should represent it.
    """

    text: str

    media: List[MediaAsset] = field(default_factory=list)

    source: Optional[str] = None
    source_url: Optional[str] = None
    article_url: Optional[str] = None

    formatting: FormattingOptions = field(
        default_factory=FormattingOptions
    )

    platform_metadata: Dict[str, Any] = field(default_factory=dict)