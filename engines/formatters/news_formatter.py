"""News Formatter - Sprint 54.

Форматирует новостной пост с переводом EN->RU через LLM.

Формат поста:
📰 Заголовок (переведён если EN)

Описание (переведено если EN)...

📍 Источник: HABR
✍️ Автор

🔗 Читать: ...

#news #tech #hashtags
"""
from typing import Any

from engines.formatters.base import (
    BaseFormatter,
    FormatContext,
    Publication,
    CAPTION_LIMIT,
    unescape,
    smart_truncate,
    translate_to_russian,
)


class NewsFormatter(BaseFormatter):
    content_type = "news"

    def format(self, news_article: Any, ctx: FormatContext) -> Publication:
        formatting = ctx.formatting
        item = ctx.item

        # 1. Title (переводим если EN)
        title_name = news_article.title
        if formatting.get("unescape_html", True):
            title_name = unescape(title_name)
        title_name = translate_to_russian(title_name, max_length=200) or title_name

        # 2. Summary (переводим если EN)
        summary = news_article.summary or ""
        if summary:
            summary = translate_to_russian(summary, max_length=500) or summary

        # 3. Tags -> hashtags
        tags = news_article.tags or []
        max_hashtags = formatting.get("max_hashtags", 8)
        hashtags = self.build_hashtags(tags, max_hashtags)

        # 4. Header
        emoji = formatting.get("emoji_header", "📰")
        header = f"{emoji} {title_name}\n\n"

        # 5. Source line
        source_line = f"📍 Источник: {news_article.source_name.upper()}\n"
        if news_article.author:
            source_line += f"✍️ {news_article.author}\n"

        # 6. Link line + hashtags
        link_url = ctx.telegraph_url or ctx.short_url or news_article.canonical_url
        link_line = f"🔗 Читать: {link_url}\n\n"
        hashtags_text = " ".join(hashtags) if hashtags else "#news"

        # 7. Description
        desc_text = ""
        if summary and formatting.get("include_description", True):
            reserved = len(header) + len(source_line) + len(link_line) + len(hashtags_text) + 10
            available = CAPTION_LIMIT - reserved
            if available > 100:
                desc_text = smart_truncate(summary, available) + "\n\n"

        text = header + desc_text + source_line + link_line + hashtags_text

        # 8. Buttons
        buttons = self.build_buttons(
            ctx,
            telegraph_text="📖 Читать полностью",
            source_text="🔗 Источник",
        )

        return Publication(
            text=text,
            image_url=ctx.image_url,
            buttons=buttons,
            source_url=news_article.canonical_url,
            metadata={"news_article_id": str(getattr(news_article, "id", ""))},
        )