"""VKRenderer — renders Publication for VK platform.

Sprint 72.3
Transforms Publication into VK-ready wall.post payload.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.models.publication import Publication, MediaAsset


logger = logging.getLogger(__name__)


@dataclass
class VKRenderResult:
    """Result of rendering Publication for VK."""

    message: str
    attachments: List[str] = field(default_factory=list)
    link: Optional[str] = None  # for "Read full" attachment

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict suitable for VK wall.post API."""
        result = {"message": self.message}
        if self.attachments:
            result["attachments"] = ",".join(self.attachments)
        if self.link:
            # Add link as attachment if no media
            if not self.attachments:
                result["attachments"] = self.link
        return result


class VKRenderer:
    """Renders Publication for VK wall.post.

    Design principles:
    - Plain text message (no HTML/Markdown)
    - Source as simple text line "Источник: TheVerge"
    - Article URL as text link at the end (or as attachment)
    - Media: VK attachment strings (photo-XXXX_YYYYY or URLs)
    """

    VK_MAX_MESSAGE_LENGTH = 16000

    def __init__(
        self,
        source_label: str = "Источник:",
        article_text: str = "Читать полностью:",
    ):
        self.source_label = source_label
        self.article_text = article_text

    def render(self, pub: Publication) -> VKRenderResult:
        """Render Publication for VK."""
        # 1. Build message
        message = self._build_message(pub)

        # 2. Build attachments
        attachments = self._build_attachments(pub)

        # 3. Article link (if no media, attach as link)
        link = None
        if pub.article_url and not attachments:
            link = pub.article_url

        return VKRenderResult(
            message=message,
            attachments=attachments,
            link=link,
        )

    def _build_message(self, pub: Publication) -> str:
        """Build VK message (plain text)."""
        message = pub.text or ""

        # Add source attribution
        if pub.source:
            source_line = f"{self.source_label} {pub.source}"
            message = f"{message}\n\n{source_line}"

        # Add article link as plain text (if URL present)
        if pub.article_url:
            message = f"{message}\n\n{self.article_text} {pub.article_url}"

        # Truncate if needed
        if len(message) > self.VK_MAX_MESSAGE_LENGTH:
            message = message[: self.VK_MAX_MESSAGE_LENGTH - 3] + "..."

        return message

    def _build_attachments(self, pub: Publication) -> List[str]:
        """Build VK attachment strings.

        VK uses URLs directly for external links.
        For uploaded media, format is "photo{owner_id}_{media_id}".
        Here we just pass URLs; actual upload happens in vk_publisher.
        """
        attachments: List[str] = []

        for asset in pub.media:
            if asset.media_type == "image" and asset.url:
                attachments.append(asset.url)
            elif asset.media_type == "video" and asset.url:
                attachments.append(asset.url)

        return attachments