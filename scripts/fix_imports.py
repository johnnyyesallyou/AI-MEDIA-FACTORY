import pathlib

p = pathlib.Path("/app/engines/source_adapters/remanga_adapter.py")
c = p.read_text(encoding="utf-8")

# 1. Фикс импорта
c = c.replace(
    "from engines.source_adapter_base import SourceAdapter, SourceItem",
    "from .base import BaseSourceAdapter, SourceItem",
    1
)

# 2. Фикс наследования
c = c.replace(
    "class ReMangaAdapter(SourceAdapter, BaseMangaAdapter):",
    "class ReMangaAdapter(BaseSourceAdapter, BaseMangaAdapter):",
    1
)

p.write_text(c, encoding="utf-8")
print("✅ Imports fixed")

# Проверка
import ast
try:
    ast.parse(c)
    print("✅ Syntax OK")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")

# Проверка что import правильный
if "from .base import BaseSourceAdapter, SourceItem" in c:
    print("✅ Correct import present")
if "class ReMangaAdapter(BaseSourceAdapter, BaseMangaAdapter):" in c:
    print("✅ Correct inheritance")