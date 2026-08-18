import pathlib
import re

p = pathlib.Path("/app/engines/source_adapters/remanga_adapter.py")
c = p.read_text(encoding="utf-8")

# 1. Добавляем импорт BaseMangaAdapter + MangaItem (если нет)
if "from engines.source_adapters.base_manga_adapter" not in c:
    c = c.replace(
        "import requests",
        "import requests\nfrom engines.source_adapters.base_manga_adapter import BaseMangaAdapter, MangaItem",
        1
    )

# 2. Наследуем от BaseMangaAdapter (если ещё не наследуем)
if "class ReMangaAdapter(BaseMangaAdapter):" not in c and "class ReMangaAdapter:" in c:
    c = c.replace(
        "class ReMangaAdapter:",
        "class ReMangaAdapter(BaseMangaAdapter):",
        1
    )

# 3. ПРАВИЛЬНАЯ вставка в конец класса (перед концом файла)
new_methods = '''
    # ========== Sprint 22: New manga adapter interface ==========

    def _to_manga_item(self, item) -> MangaItem:
        """Конвертирует SourceItem в MangaItem."""
        return MangaItem(
            external_id=item.chapter_id or item.title_id,
            title=item.title_name or "Unknown",
            chapter=item.chapter_number or "?",
            url=item.chapter_url or item.title_url,
            language="ru",
            source="remanga",
            description=None,
            genres=None,
            cover_url=item.cover_url,
            title_slug=item.title_slug,
            title_name_en=item.title_name_en,
            chapter_id=item.chapter_id,
            title_url=item.title_url,
            upload_date=item.upload_date,
        )

    def fetch_latest_chapters_manga(self, limit: int = 20) -> list:
        """Возвращает List[MangaItem] (новый интерфейс)."""
        source_items = self.fetch_latest_chapters(limit)
        return [self._to_manga_item(item) for item in source_items]
'''

# Проверяем что новых методов ещё нет
if "_to_manga_item" not in c:
    # Вставляем в конец файла (после всех методов класса)
    c = c.rstrip() + "\n" + new_methods
    print("✅ Methods added at end of file")
else:
    print("ℹ️ Methods already exist")

p.write_text(c, encoding="utf-8")

import ast
try:
    ast.parse(c)
    print("✅ Syntax OK")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")

# Проверка: сколько раз встречается def _parse_item
parse_count = c.count("def _parse_item")
print(f"def _parse_item count: {parse_count} (should be 1)")