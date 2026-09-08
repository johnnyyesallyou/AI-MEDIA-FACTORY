"""PublicationBuilder — builds platform-independent Publication from content dict.

Sprint 72.2
Transforms internal content representation into canonical Publication object
ready for platform-specific rendering (Telegram, VK, etc).
"""

import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from core.models.publication import (
    FormattingOptions,
    MediaAsset,
    Publication,
)

logger = logging.getLogger(__name__)


# Archetype-based defaults for publication policies
ARCHETYPE_DEFAULTS = {
    "news": {
        "source_link": "always",        # always | optional | never
        "article_link": "conditional",  # always | conditional | never
        "media_policy": "preferred",    # required | preferred | optional | none
        "max_length": 700,
        "max_paragraphs": 4,
        "emojis": False,
        "allow_bullets": True,
    },
    "educational": {
        "source_link": "optional",
        "article_link": "never",
        "media_policy": "preferred",
        "max_length": 800,
        "max_paragraphs": 5,
        "emojis": False,
        "allow_bullets": True,
    },
    "entertainment": {
        "source_link": "never",
        "article_link": "never",
        "media_policy": "required",
        "max_length": 400,
        "max_paragraphs": 3,
        "emojis": True,
        "allow_bullets": False,
    },
    "viral": {
        "source_link": "never",
        "article_link": "never",
        "media_policy": "required",
        "max_length": 300,
        "max_paragraphs": 2,
        "emojis": True,
        "allow_bullets": False,
    },
    "releases": {
        "source_link": "always",
        "article_link": "never",
        "media_policy": "required",
        "max_length": 500,
        "max_paragraphs": 3,
        "emojis": False,
        "allow_bullets": True,
    },
    "reviews": {
        "source_link": "always",
        "article_link": "always",
        "media_policy": "required",
        "max_length": 1000,
        "max_paragraphs": 6,
        "emojis": False,
        "allow_bullets": True,
    },
    "community": {
        "source_link": "never",
        "article_link": "never",
        "media_policy": "optional",
        "max_length": 400,
        "max_paragraphs": 3,
        "emojis": True,
        "allow_bullets": True,
    },
    "aggregator": {
        "source_link": "always",
        "article_link": "always",
        "media_policy": "preferred",
        "max_length": 400,
        "max_paragraphs": 3,
        "emojis": False,
        "allow_bullets": True,
    },
}

# Fallback if archetype unknown
DEFAULT_POLICY = ARCHETYPE_DEFAULTS["news"]


class PublicationBuilder:
    """Builds Publication from content dict + channel profile.

    Design principle:
    - Explicit profile settings override archetype defaults
    - Archetype defaults override global defaults
    - Never mutates the input content dict
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PublicationBuilder")

    def build(
        self,
        post: Dict[str, Any],
        profile: Optional[Any] = None,
        channel: Optional[Any] = None,
    ) -> Publication:
        """Build Publication from content dict.

        Args:
            post: content dict with keys: title, content, url, summary, ...
            profile: ChannelProfileORM (optional)
            channel: ChannelORM (optional, used for platform metadata)

        Returns:
            Publication object ready for platform rendering
        """
        # 1. Determine archetype
        archetype = self._get_archetype(profile)
        policy = self._get_policy(profile, archetype)

        # 2. Build text (without source/article info - those are metadata)
        text = self._build_text(post, policy)

        # 3. Build media list
        media = self._build_media(post, policy)

        # 4. Determine source metadata
        source, source_url = self._resolve_source(post, policy)

        # 5. Determine article_url (for "read full" button)
        article_url = self._resolve_article_url(post, policy, text)

        # 6. Build formatting options
        formatting = FormattingOptions(
            max_length=policy["max_length"],
            max_paragraphs=policy["max_paragraphs"],
            emojis=policy["emojis"],
            allow_bullets=policy["allow_bullets"],
        )

        # 7. Platform metadata (for renderers)
        platform = getattr(channel, "platform", "telegram") if channel else "telegram"
        platform_metadata = {
            "platform": platform,
            "archetype": archetype,
            "policy": policy,
        }

        pub = Publication(
            text=text,
            media=media,
            source=source,
            source_url=source_url,
            article_url=article_url,
            formatting=formatting,
            platform_metadata=platform_metadata,
        )

        self.logger.debug(
            f"Built Publication: archetype={archetype}, "
            f"text_len={len(text)}, media={len(media)}, "
            f"source={source}, article_url={bool(article_url)}"
        )
        return pub

    # ---------- Internal helpers ----------

    def _get_archetype(self, profile: Optional[Any]) -> str:
        if profile is None:
            return "news"
        archetype = getattr(profile, "archetype", None)
        if archetype and archetype in ARCHETYPE_DEFAULTS:
            return archetype
        return "news"

    def _get_policy(self, profile: Optional[Any], archetype: str) -> Dict[str, Any]:
        """Merge: defaults ← archetype defaults ← profile overrides."""
        policy = dict(ARCHETYPE_DEFAULTS.get(archetype, DEFAULT_POLICY))

        if profile is None:
            return policy

        # Override from profile.content_profile.publishing (if exists)
        cp = getattr(profile, "content_profile", None)
        if isinstance(cp, dict):
            pub_settings = cp.get("publishing", {})
            if isinstance(pub_settings, dict):
                for key in ["source_link", "article_link", "media_policy"]:
                    if key in pub_settings:
                        policy[key] = pub_settings[key]

        # Override from profile.publishing JSONB column (if exists)
        pub_col = getattr(profile, "publishing", None)
        if isinstance(pub_col, dict):
            for key in ["source_link", "article_link", "media_policy"]:
                if key in pub_col:
                    policy[key] = pub_col[key]

        return policy

    def _build_text(self, post: Dict[str, Any], policy: Dict[str, Any]) -> str:
        """Build text from post content.

        IMPORTANT: does NOT include source or article link - those are metadata
        that renderers will add if needed.
        """
        # Use draft_text or content field
        text = post.get("content") or post.get("draft_text") or ""

        if not text:
            # Fallback to title + summary
            title = post.get("title") or post.get("headline") or ""
            summary = post.get("summary") or ""
            text = f"{title}\n\n{summary}".strip() if summary else title

        # Enforce max_paragraphs
        if policy.get("allow_bullets", True) is False:
            # Split into paragraphs, limit, rejoin
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            max_p = policy.get("max_paragraphs", 4)
            if len(paragraphs) > max_p:
                text = "\n\n".join(paragraphs[:max_p])

        # Enforce max_length
        max_len = policy.get("max_length", 700)
        if len(text) > max_len:
            # Smart truncate at word boundary
            truncated = text[:max_len].rsplit(" ", 1)[0]
            text = truncated + "..."

        return text.strip()

    def _build_media(
        self, post: Dict[str, Any], policy: Dict[str, Any]
    ) -> List[MediaAsset]:
        """Extract media assets from post."""
        media: List[MediaAsset] = []
        media_policy = policy.get("media_policy", "preferred")

        if media_policy == "none":
            return media

        # image_url
        image_url = post.get("image_url") or post.get("media_url")
        if image_url:
            media.append(MediaAsset(url=image_url, media_type="image"))

        # image_urls (list)
        for url in post.get("image_urls", []) or []:
            if url and url not in [m.url for m in media]:
                media.append(MediaAsset(url=url, media_type="image"))

        # video_url
        video_url = post.get("video_url")
        if video_url:
            media.append(MediaAsset(url=video_url, media_type="video"))

        return media

    def _resolve_source(
        self, post: Dict[str, Any], policy: Dict[str, Any]
    ) -> tuple[Optional[str], Optional[str]]:
        """Determine source name and URL based on policy."""
        source_policy = policy.get("source_link", "always")

        if source_policy == "never":
            return None, None

        # Try to extract source from post
        source_url = post.get("url") or post.get("source_url")
        source_name = post.get("source") or post.get("source_name")

        # Auto-detect source name from URL if not provided
        if source_url and not source_name:
            source_name = self._extract_source_name(source_url)

        if source_policy == "always":
            return source_name, source_url
        elif source_policy == "optional":
            # Only include if we have meaningful data
            if source_name and source_url:
                return source_name, source_url
            return None, None

        return None, None

    def _resolve_article_url(
        self, post: Dict[str, Any], policy: Dict[str, Any], text: str
    ) -> Optional[str]:
        """Determine if we need a 'read full article' link."""
        article_policy = policy.get("article_link", "conditional")

        if article_policy == "never":
            return None

        source_url = post.get("url") or post.get("source_url")

        if article_policy == "always":
            return source_url

        if article_policy == "conditional":
            # Add link only if text was truncated or content is long
            original_len = len(post.get("content") or post.get("draft_text") or "")
            max_len = policy.get("max_length", 700)
            if original_len > max_len * 1.2:  # was truncated by >20%
                return source_url
            # Or if there's a telegraph_url (long-form version)
            telegraph = post.get("telegraph_url")
            if telegraph:
                return telegraph
            return None

        return None

    @staticmethod
    def _extract_source_name(url: str) -> Optional[str]:
        """Extract human-readable source name from URL."""
        if not url:
            return None
        try:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc
            # Strip www.
            if domain.startswith("www."):
                domain = domain[4:]
            # Take the main part
            parts = domain.split(".")
            if len(parts) >= 2:
                return parts[-2].title()
            return domain.title()
        except Exception:
            return None