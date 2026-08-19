import pathlib

p = pathlib.Path("/app/engines/source_adapters/mangadex_adapter.py")
c = p.read_text(encoding="utf-8")

# 1. Импорт BaseMangaAdapter + MangaItem
if "from .base_manga_adapter" not in c:
    c = c.replace(
        "from .base import BaseSourceAdapter, SourceItem",
        "from .base import BaseSourceAdapter, SourceItem\nfrom .base_manga_adapter import BaseMangaAdapter, MangaItem",
        1
    )

# 2. Наследование
if "class MangaDexAdapter(BaseSourceAdapter):" in c:
    c = c.replace(
        "class MangaDexAdapter(BaseSourceAdapter):",
        "class MangaDexAdapter(BaseSourceAdapter, BaseMangaAdapter):",
        1
    )

# 3. Новые методы в конец файла
new_methods = '''
    # ========== Sprint 22: New manga adapter interface ==========

    def _to_manga_item(self, item) -> "MangaItem":
        """Конвертирует SourceItem в MangaItem."""
        return MangaItem(
            external_id=item.chapter_id or item.title_id,
            title=item.title_name or "Unknown",
            chapter=item.chapter_number or "?",
            url=item.chapter_url or item.title_url,
            language="ru",
            source="mangadex",
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

if "_to_manga_item" not in c:
    c = c.rstrip() + "\n" + new_methods
    print("✅ Methods added")
else:
    print("ℹ️ Methods already exist")

p.write_text(c, encoding="utf-8")

import ast
try:
    ast.parse(c)
    print("✅ Syntax OK")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")