"""Anime Formatter - Sprint 54.

Форматирует пост для новости/релиза аниме с переводом EN->RU.

Формат поста:
🎬 Название
🌐 English / 日本語

📅 Fall 2026
📺 Ongoing
🎞️ 12 episodes

Описание (переведено если strip_non_ru)...

🔗 Подробнее: ...

#жанры #теги
"""
from typing import Any, List

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

        # 1. Title name
        title_name = self._get_title_name(anime_title, item)
        if formatting.get("unescape_html", True):
            title_name = unescape(title_name)

        # 2. Description (перевод если strip_non_ru и текст не содержит кириллицу)
        description = anime_title.description or ""
        if publishing_policy.get("strip_non_ru_description") and not has_cyrillic(description):
            description = translate_to_russian(description)

        # 3. Genres -> hashtags
        genres = anime_title.genres or []
        max_hashtags = formatting.get("max_hashtags", 10)
        hashtags = self.build_hashtags(genres, max_hashtags)

        # 4. Header + aliases
        emoji = formatting.get("emoji_header", "🎬")
        header = f"{emoji} {title_name}\n"
        if anime_title.aliases:
            if "en" in anime_title.aliases and anime_title.aliases["en"] != title_name:
                header += f"🌐 {anime_title.aliases['en']}\n"
            elif "ja" in anime_title.aliases:
                header += f"🌐 {anime_title.aliases['ja']}\n"
        header += "\n"

        # 5. Season line
        season_line = ""
        if anime_title.season and anime_title.season_year:
            season_line = f"📅 {anime_title.season} {anime_title.season_year}\n"
        if anime_title.status:
            season_line += f"📺 {anime_title.status}\n"
        if anime_title.episodes:
            season_line += f"🎞️ {anime_title.episodes} episodes\n"

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
            source_url=item.source_url,
            metadata={"anime_episode_id": getattr(item, "anime_episode_id", None)},
        )

    def _get_title_name(self, anime_title, item) -> str:
        name = anime_title.title_ru or anime_title.title or ""
        return name or (getattr(item, "headline", "") or "")