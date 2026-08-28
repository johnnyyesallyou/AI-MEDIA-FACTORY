"""Anime Formatter - Sprint 54 (fixed Sprint 59).

Форматирует пост для новости/релиза аниме с переводом EN->RU.
ВСЕ атрибуты читаются через getattr — совместимо с любой моделью AnimeTitle.
"""
import json
from typing import Any

from engines.formatters.base import (
    BaseFormatter,
    FormatContext,
    Publication,
    CAPTION_LIMIT,
    unescape,
    smart_truncate,
    translate_to_russian,
    has_cyrillic,
)


class AnimeFormatter(BaseFormatter):
    content_type = "anime"

    def format(self, anime_title: Any, ctx: FormatContext) -> Publication:
        item = ctx.item
        formatting = ctx.formatting
        publishing_policy = ctx.publishing_policy

        def g(name, default=None):
            return getattr(anime_title, name, default)

        # 1. Title name (безопасно)
        title_name = self._get_title_name(anime_title, item)
        if formatting.get("unescape_html", True):
            title_name = unescape(title_name)

        # 2. Description (перевод если strip_non_ru и нет кириллицы)
        description = g("description") or ""
        if publishing_policy.get("strip_non_ru_description") and not has_cyrillic(description):
            description = translate_to_russian(description)

        # 3. Genres -> hashtags
        genres = g("genres") or []
        max_hashtags = formatting.get("max_hashtags", 10)
        hashtags = self.build_hashtags(genres, max_hashtags)

        # 4. Header + aliases (безопасно)
        emoji = formatting.get("emoji_header", "🎬")
        header = f"{emoji} {title_name}\n"
        aliases = g("aliases") or {}
        if isinstance(aliases, dict):
            if aliases.get("en") and aliases["en"] != title_name:
                header += f"🌐 {aliases['en']}\n"
            elif aliases.get("ja"):
                header += f"🌐 {aliases['ja']}\n"
        header += "\n"

        # 5. Season line (безопасно)
        season_line = ""
        season = g("season")
        season_year = g("season_year")
        if season and season_year:
            season_line = f"📅 {season} {season_year}\n"
        if g("status"):
            season_line += f"📺 {g('status')}\n"
        if g("episodes"):
            season_line += f"🎞️ {g('episodes')} episodes\n"

        # 6. Link line + hashtags
        link_url = ctx.telegraph_url or ctx.short_url
        link_line = f"🔗 Подробнее: {link_url}\n\n" if link_url else ""
        hashtags_text = " ".join(hashtags) if hashtags else "#аниме"

        # 7. Description (smart truncate)
        desc_text = ""
        if description and formatting.get("include_description", True):
            reserved = len(header) + len(season_line) + len(link_line) + len(hashtags_text) + 10
            available = CAPTION_LIMIT - reserved
            if available > 100:
                desc_text = smart_truncate(description, available) + "\n\n"

        text = header + season_line + desc_text + link_line + hashtags_text

        # 8. Buttons
        buttons = self.build_buttons(
            ctx,
            telegraph_text="📖 Читать на Telegraph",
            source_text="🔗 AniList",
        )

        return Publication(
            text=text,
            image_url=ctx.image_url,
            buttons=buttons,
            source_url=getattr(item, "source_url", None),
            metadata={"anime_episode_id": getattr(item, "anime_episode_id", None)},
        )

    def _get_title_name(self, anime_title: Any, item: Any) -> str:
        """Безопасное получение названия: meta -> title_ru -> title -> headline."""
        meta = {}
        try:
            meta = json.loads(getattr(item, "source_text", None) or "{}")
        except Exception:
            meta = {}

        name = (
            meta.get("title_ru")
            or meta.get("ru_title")
            or getattr(anime_title, "title_ru", None)
            or getattr(anime_title, "title", None)
            or ""
        )
        return name or (getattr(item, "headline", "") or "")