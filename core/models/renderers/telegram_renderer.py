"""TelegramRenderer — renders Publication for Telegram platform.

Sprint 72.3
Transforms Publication into Telegram-ready message with:
- Natural text flow (no template headers)
- Optional inline source attribution
- Optional "Read full" button (InlineKeyboardMarkup)
- Media attachments (photo/video)
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.models.publication import Publication, MediaAsset


logger = logging.getLogger(__name__)


@dataclass
class TelegramRenderResult:
    """Result of rendering Publication for Telegram."""

    text: str
    parse_mode: Optional[str] = None
    reply_markup: Optional[Dict[str, Any]] = None
    media: List[MediaAsset] = field(default_factory=list)
    disable_web_page_preview: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict suitable for python-telegram-bot or httpx."""
        result = {
            "text": self.text,
            "parse_mode": self.parse_mode,
            "disable_web_page_preview": self.disable_web_page_preview,
        }
        if self.reply_markup:
            result["reply_markup"] = self.reply_markup
        return result


class TelegramRenderer:
    """Renders Publication for Telegram.

    Design principles:
    - Natural text: no emojis like 🔥📌📊, no template headers
    - Source attribution as simple paragraph at the end (if configured)
    - Article URL as inline button "Читать полностью" (if configured)
    - Media: list of photos/videos for album/send_photo/send_video
    """

    TELEGRAM_MAX_LENGTH = 4096

    def __init__(
        self,
        source_label: str = "Источник:",
        article_button_text: str = "Читать полностью",
        source_emoji: Optional[str] = None,
    ):
        self.source_label = source_label
        self.article_button_text = article_button_text
        self.source_emoji = source_emoji

    def render(self, pub: Publication) -> TelegramRenderResult:
        """Render Publication for Telegram."""
        # 1. Build text (clean + optional source attribution)
        text = self._build_text(pub)

        # 2. Build inline keyboard for article_url
        reply_markup = self._build_reply_markup(pub)

        # 3. Collect media
        media = list(pub.media)

        # 4. Disable web page preview if we have article button
        disable_preview = pub.article_url is not None

        return TelegramRenderResult(
            text=text,
            parse_mode="HTML",
            reply_markup=reply_markup,
            media=media,
            disable_web_page_preview=disable_preview,
        )

    def _build_text(self, pub: Publication) -> str:
        """Build clean text with optional source attribution.

        IMPORTANT: escape main text FIRST, then add HTML source line.
        Otherwise HTML tags in source attribution get escaped.
        """
        text = pub.text or ""

        # Step 1: Escape main text FIRST (before adding source)
        text = self._escape_html(text)

        # Step 2: Add source as separate paragraph (HTML already prepared)
        if pub.source:
            source_line = self._format_source_line(pub)
            text = f"{text}\n\n{source_line}"

        # Step 3: Hard truncate if exceeds Telegram limit
        if len(text) > self.TELEGRAM_MAX_LENGTH:
            text = text[: self.TELEGRAM_MAX_LENGTH - 3] + "..."

        return text

    def _format_source_line(self, pub: Publication) -> str:
        """Format source attribution line.

        News style: "Источник: TheVerge"
        With emoji: "🔗 Источник: TheVerge"
        With clickable link: "Источник: <a href='url'>TheVerge</a>"

        NOTE: Returns HTML-ready string. Caller must NOT escape this.
        """
        source = pub.source or ""

        if pub.source_url:
            escaped_url = self._escape_html_attr(pub.source_url)
            escaped_source = self._escape_html(source)
            source_text = f'<a href="{escaped_url}">{escaped_source}</a>'
        else:
            source_text = self._escape_html(source)

        label = self._escape_html(self.source_label)

        if self.source_emoji:
            return f"{self.source_emoji} {label} {source_text}"
        return f"{label} {source_text}"

    def _build_reply_markup(
        self, pub: Publication
    ) -> Optional[Dict[str, Any]]:
        """Build InlineKeyboardMarkup for article_url button."""
        if not pub.article_url:
            return None

        return {
            "inline_keyboard": [
                [
                    {
                        "text": self.article_button_text,
                        "url": pub.article_url,
                    }
                ]
            ]
        }

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters for Telegram parse_mode=HTML."""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    @staticmethod
    def _escape_html_attr(text: str) -> str:
        """Escape for HTML attribute (URLs)."""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )