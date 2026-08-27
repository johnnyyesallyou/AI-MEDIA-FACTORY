"""Manga Formatter - Sprint 54.

Форматирует пост для публикации новой главы манги.

Формат поста:
📚 Название
🌐 Original title

Описание...

📖 Глава XX (или "Новые главы: 1, 2, 3" если несколько)
🔗 Читать: ...

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
)


class MangaFormatter(BaseFormatter):
    content_type = "manga"

    def format(self, manga_title: Any, ctx: FormatContext) -> Publication:
        """Строит Publication из MangaTitle + Context."""
        meta = ctx.meta
        related_items = ctx.related_items or []
        formatting = ctx.formatting
        item = ctx.item

        # 1. Chapter number
        chapter_number = meta.get("manga_chapter_number", "?")

        # 2. Title name
        title_name = self._get_title_name(manga_title, item)
        if formatting.get("unescape_html", True):
            title_name = unescape(title_name)

        # 3. Description
        description = unescape(manga_title.description or "")
        if ctx.publishing_policy.get("strip_non_ru_description"):
            import re
            if not re.search(r"[а-яА-ЯёЁ]", description):
                description = ""

        # 4. Genres -> hashtags
        genres = manga_title.genres or []
        max_hashtags = formatting.get("max_hashtags", 10)
        hashtags = self.build_hashtags(genres, max_hashtags)

        # 5. Chapters from related items
        chapters = []
        for rel in related_items:
            rel_meta = self._meta_for(rel)
            if rel_meta.get("manga_chapter_number"):
                chapters.append(rel_meta["manga_chapter_number"])
        chapters = sorted(
            set(chapters),
            key=lambda x: float(x) if x.replace('.', '').isdigit() else 0,
        )

        # 6. Header
        emoji = formatting.get("emoji_header", "📚")
        header = f"{emoji} {title_name}\n"
        if manga_title.aliases and "en" in manga_title.aliases:
            en_name = unescape(manga_title.aliases["en"])
            if en_name != title_name:
                header += f"🌐 {en_name}\n"
        header += "\n"

        # 7. Chapter line
        if len(chapters) > 1:
            chapter_line = f"📖 Новые главы: {', '.join(chapters)}\n"
        else:
            chapter_line = f"📖 Глава {chapter_number}\n"

        # 8. Link line + hashtags
        link_url = ctx.telegraph_url or ctx.short_url
        link_line = f"🔗 Читать: {link_url}\n\n"
        hashtags_text = " ".join(hashtags) if hashtags else "#манга"

        # 9. Description (smart truncate)
        desc_text = ""
        if description and formatting.get("include_description", True):
            reserved = len(header) + len(chapter_line) + len(link_line) + len(hashtags_text) + 10
            available = CAPTION_LIMIT - reserved
            if available > 100:
                desc_text = smart_truncate(description, available) + "\n\n"

        # 10. Full text
        text = header + desc_text + chapter_line + link_line + hashtags_text

        # 11. Buttons
        buttons = self.build_buttons(
            ctx,
            telegraph_text="📖 Читать на Telegraph",
            source_text="🔗 Источник",
        )

        return Publication(
            text=text,
            image_url=ctx.image_url,
            buttons=buttons,
            source_url=item.source_url,
            metadata={"manga_chapter_id": getattr(item, "manga_chapter_id", None)},
        )

    # ---- helpers ----

    def _get_title_name(self, manga_title, item) -> str:
        """Берёт название из MangaTitle.title_ru (RU) или MangaTitle.title (EN)."""
        name = manga_title.title_ru or manga_title.title or ""
        return name or (getattr(item, "headline", "") or "")

    def _meta_for(self, item) -> dict:
        import json
        try:
            return json.loads(getattr(item, "source_text", None) or "{}")
        except Exception:
            return {}