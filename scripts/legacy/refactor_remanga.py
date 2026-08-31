import pathlib, re

p = pathlib.Path("/app/engines/source_adapters/remanga_adapter.py")
c = p.read_text(encoding="utf-8")

# 1. Добавляем импорт BaseMangaAdapter + MangaItem
if "from engines.source_adapters.base_manga_adapter" not in c:
    c = c.replace(
        "import requests",
        "import requests\nfrom engines.source_adapters.base_manga_adapter import BaseMangaAdapter, MangaItem",
        1
    )

# 2. Наследуем от BaseMangaAdapter
c = c.replace(
    "class ReMangaAdapter:",
    "class ReMangaAdapter(BaseMangaAdapter):",
    1
)

# 3. Добавляем конвертацию в MangaItem в конец fetch_latest_chapters
# Ищем return items и добавляем конвертацию перед ним
if "def _to_manga_item" not in c:
    converter = '''
    def _to_manga_item(self, item: "SourceItem") -> MangaItem:
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
            upload_date=item.upload_date
        )

    def fetch_latest_chapters_manga(self, limit: int = 20) -> List[MangaItem]:
        """Возвращает List[MangaItem] (новый интерфейс)."""
        source_items = self.fetch_latest_chapters(limit)
        return [self._to_manga_item(item) for item in source_items]
'''
    
    # Вставляем перед последним def (или в конец класса)
    lines = c.splitlines(keepends=True)
    # Находим последнюю строку класса
    for i in range(len(lines)-1, -1, -1):
        if lines[i].startswith("    def "):
            # Вставляем после этого метода (находим следующую строку без отступа)
            insert_pos = i + 1
            while insert_pos < len(lines) and lines[insert_pos].startswith("        "):
                insert_pos += 1
            lines.insert(insert_pos, converter)
            break
    c = "".join(lines)

p.write_text(c, encoding="utf-8")

import ast
try:
    ast.parse(c)
    print("✅ ReMangaAdapter refactored (syntax OK)")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")