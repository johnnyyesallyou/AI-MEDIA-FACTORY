import pathlib

p = pathlib.Path("/app/backend/automation/jobs/news_publish_job.py")
c = p.read_text(encoding="utf-8")

# 1. Добавляем импорт formatter
if "from engines.formatters import" not in c:
    c = c.replace(
        "from engines.publishing import (",
        "from engines.formatters import NewsFormatter, FormatContext\nfrom engines.publishing import (",
    )
    print("[OK] Added formatter import")

# 2. Заменяем _build_publication (ищем начало метода)
# Так как метод большой, используем regex-подобный подход
import re

# Находим начало метода
start_pattern = r'    def _build_publication\('
match = re.search(start_pattern, c)
if match:
    start_pos = match.start()
    
    # Находим конец метода (следующий def на том же уровне)
    next_def = c.find('\n    def ', start_pos + 10)
    if next_def == -1:
        next_def = len(c)
    
    # Заменяем метод
    new_method = '''    def _build_publication(
        self,
        news_article: NewsArticle,
        item: ContentORM,
        telegraph_url: Optional[str],
        short_url: str,
        image_url: Optional[str],
        formatting: dict,
        publishing_policy: dict,
    ) -> Publication:
        """Sprint 54: делегируем форматирование в NewsFormatter."""
        formatter = NewsFormatter()
        ctx = FormatContext(
            item=item,
            meta=self._meta(item),
            related_items=[],
            telegraph_url=telegraph_url,
            short_url=short_url,
            image_url=image_url,
            formatting=formatting,
            publishing_policy=publishing_policy,
        )
        return formatter.format(news_article, ctx)
'''
    
    c = c[:start_pos] + new_method + c[next_def:]
    p.write_text(c, encoding="utf-8")
    print("[OK] NewsPublishJob._build_publication refactored to use NewsFormatter")
else:
    print("[!] Pattern not found")