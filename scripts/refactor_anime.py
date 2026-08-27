import pathlib, re

p = pathlib.Path("/app/backend/automation/jobs/anime_publish_job.py")
c = p.read_text(encoding="utf-8")

# 1. Добавляем импорт formatter
if "from engines.formatters import" not in c:
    c = c.replace(
        "from engines.publishing import (",
        "from engines.formatters import AnimeFormatter, FormatContext\nfrom engines.publishing import (",
    )
    print("[OK] Added formatter import")

# 2. Заменяем _build_publication
start_pattern = r'    def _build_publication\('
match = re.search(start_pattern, c)
if match:
    start_pos = match.start()
    next_def = c.find('\n    def ', start_pos + 10)
    if next_def == -1:
        next_def = len(c)
    
    new_method = '''    def _build_publication(
        self,
        anime_title: AnimeTitle,
        item: ContentORM,
        related_items: List[ContentORM],
        telegraph_url: Optional[str],
        short_url: str,
        image_url: Optional[str],
        formatting: dict,
        publishing_policy: dict,
    ) -> Publication:
        """Sprint 54: делегируем форматирование в AnimeFormatter."""
        formatter = AnimeFormatter()
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
        return formatter.format(anime_title, ctx)
'''
    
    c = c[:start_pos] + new_method + c[next_def:]
    p.write_text(c, encoding="utf-8")
    print("[OK] AnimePublishJob._build_publication refactored to use AnimeFormatter")
else:
    print("[!] Pattern not found")