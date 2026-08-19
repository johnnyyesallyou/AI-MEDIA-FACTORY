import pathlib

p = pathlib.Path("/app/engines/source_adapters/manga_registry.py")
c = p.read_text(encoding="utf-8")

# Импорт
if "ReadMangaAdapter" not in c:
    c = c.replace(
        "from .mangadex_adapter import MangaDexAdapter",
        "from .mangadex_adapter import MangaDexAdapter\nfrom .readmanga_adapter import ReadMangaAdapter",
        1,
    )

# Регистрация
if '"readmanga":' not in c:
    c = c.replace(
        '"mangadex": MangaDexAdapter(),',
        '"mangadex": MangaDexAdapter(),\n        "readmanga": ReadMangaAdapter(),',
        1,
    )

p.write_text(c, encoding="utf-8")
print("✅ ReadManga registered in MangaRegistry")