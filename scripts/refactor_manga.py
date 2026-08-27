import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

# 1. Добавляем импорт formatter
if "from engines.formatters import" not in c:
    c = c.replace(
        "from engines.publishing import (",
        "from engines.formatters import MangaFormatter, FormatContext\nfrom engines.publishing import (",
    )
    print("[OK] Added formatter import")

# 2. Заменяем _build_publication на делегирование в MangaFormatter
old_method = '''    def _build_publication(
        self,
        manga_title: MangaTitle,
        item: ContentORM,
        related_items: List[ContentORM],
        telegraph_url: Optional[str],
        short_url: str,
        image_url: Optional[str],
        formatting: dict,
        publishing_policy: dict,
    ) -> Publication:
        meta = self._meta(item)
        chapter_number = meta.get("manga_chapter_number", "?")
        title_name = self._get_title_name(manga_title, item)

        # unescape HTML entities (fixes &quot; etc.)
        if formatting.get("unescape_html", True):
            title_name = html_lib.unescape(title_name)

        description = html_lib.unescape(manga_title.description or "")
        if publishing_policy.get("strip_non_ru_description") and not re.search(r"[а-яА-ЯёЁ]", description):
            description = ""

        genres = manga_title.genres or []
        max_hashtags = formatting.get("max_hashtags", 10)

        chapters = []
        for rel in related_items:
            m = self._meta(rel)
            if m.get("manga_chapter_number"):
                chapters.append(m["manga_chapter_number"])
        chapters = sorted(set(chapters), key=lambda x: float(x) if x.replace('.','').isdigit() else 0)

        hashtags = [self._format_hashtag(g) for g in genres[:max_hashtags]]
        hashtags = [h for h in hashtags if h]

        emoji = formatting.get("emoji_header", "📚")
        header = f"{emoji} {title_name}\\n"
        if manga_title.aliases and "en" in manga_title.aliases:
            en_name = html_lib.unescape(manga_title.aliases["en"])
            if en_name != title_name:
                header += f"🌐 {en_name}\\n"
        header += "\\n"

        chapter_line = (
            f"📖 Новые главы: {', '.join(chapters)}\\n"
            if len(chapters) > 1 else
            f"📖 Глава {chapter_number}\\n"
        )

        link_url = telegraph_url or short_url
        link_line = f"🔗 Читать: {link_url}\\n\\n"
        hashtags_text = " ".join(hashtags) if hashtags else "#манга"

        desc_text = ""
        if description and formatting.get("include_description", True):
            reserved = len(header) + len(chapter_line) + len(link_line) + len(hashtags_text) + 10
            available = CAPTION_LIMIT - reserved
            if available > 100:
                desc_text = self._smart_truncate(description, available) + "\\n\\n"

        text = header + desc_text + chapter_line + link_line + hashtags_text

        # inline buttons
        buttons: List[PublicationButton] = []
        if publishing_policy.get("inline_buttons"):
            if telegraph_url:
                buttons.append(PublicationButton(text="📖 Читать на Telegraph", url=telegraph_url))
            if short_url and short_url != telegraph_url:
                buttons.append(PublicationButton(text="🔗 Источник", url=short_url))

        return Publication(
            text=text,
            image_url=image_url,
            buttons=buttons,
            source_url=item.source_url,
            metadata={"manga_chapter_id": item.manga_chapter_id},
        )'''

new_method = '''    def _build_publication(
        self,
        manga_title: MangaTitle,
        item: ContentORM,
        related_items: List[ContentORM],
        telegraph_url: Optional[str],
        short_url: str,
        image_url: Optional[str],
        formatting: dict,
        publishing_policy: dict,
    ) -> Publication:
        """Sprint 54: делегируем форматирование в MangaFormatter."""
        formatter = MangaFormatter()
        ctx = FormatContext(
            item=item,
            meta=self._meta(item),
            related_items=related_items,
            telegraph_url=telegraph_url,
            short_url=short_url,
            image_url=image_url,
            formatting=formatting,
            publishing_policy=publishing_policy,
        )
        return formatter.format(manga_title, ctx)'''

if old_method in c:
    c = c.replace(old_method, new_method, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] MangaPublishJob._build_publication refactored to use MangaFormatter")
else:
    print("[!] Pattern not found - manual refactor needed")