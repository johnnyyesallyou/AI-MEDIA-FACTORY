import pathlib

# 1. ReadMangaAdapter
p = pathlib.Path("/app/engines/source_adapters/readmanga_adapter.py")
c = p.read_text(encoding="utf-8")

if "from core.retry import" not in c:
    c = c.replace(
        "import requests",
        "import requests\nfrom core.retry import retry_external_api",
        1,
    )
    
    # Добавляем @retry_external_api к fetch_latest_chapters
    c = c.replace(
        "    def fetch_latest_chapters(self, limit: int = 20)",
        "    @retry_external_api\n    def fetch_latest_chapters(self, limit: int = 20)",
        1,
    )
    
    # Добавляем к get_title_info
    c = c.replace(
        "    def get_title_info(self, slug: str)",
        "    @retry_external_api\n    def get_title_info(self, slug: str)",
        1,
    )
    
    p.write_text(c, encoding="utf-8")
    print("✅ ReadMangaAdapter: retry added")
else:
    print("ℹ️ ReadMangaAdapter: already patched")

# 2. AniListAdapter
p2 = pathlib.Path("/app/engines/source_adapters/anilist_adapter.py")
c2 = p2.read_text(encoding="utf-8")

if "from core.retry import" not in c2:
    c2 = c2.replace(
        "import requests",
        "import requests\nfrom core.retry import retry_external_api",
        1,
    )
    
    # Добавляем ко всем fetch методам
    for method in ["fetch_trending_anime", "fetch_currently_airing", "get_anime_info"]:
        c2 = c2.replace(
            f"    def {method}(",
            f"    @retry_external_api\n    def {method}(",
            1,
        )
    
    p2.write_text(c2, encoding="utf-8")
    print("✅ AniListAdapter: retry added")
else:
    print("ℹ️ AniListAdapter: already patched")

# 3. ReMangaAdapter
p3 = pathlib.Path("/app/engines/source_adapters/remanga_adapter.py")
c3 = p3.read_text(encoding="utf-8")

if "from core.retry import" not in c3:
    c3 = c3.replace(
        "import requests",
        "import requests\nfrom core.retry import retry_external_api",
        1,
    )
    
    # Добавляем к fetch методу
    c3 = c3.replace(
        "    def fetch_latest_chapters_manga(",
        "    @retry_external_api\n    def fetch_latest_chapters_manga(",
        1,
    )
    
    p3.write_text(c3, encoding="utf-8")
    print("✅ ReMangaAdapter: retry added")
else:
    print("ℹ️ ReMangaAdapter: already patched")

# 4. MangaDexAdapter
p4 = pathlib.Path("/app/engines/source_adapters/mangadex_adapter.py")
c4 = p4.read_text(encoding="utf-8")

if "from core.retry import" not in c4:
    c4 = c4.replace(
        "import requests",
        "import requests\nfrom core.retry import retry_external_api",
        1,
    )
    
    c4 = c4.replace(
        "    def fetch_latest_chapters_manga(",
        "    @retry_external_api\n    def fetch_latest_chapters_manga(",
        1,
    )
    
    p4.write_text(c4, encoding="utf-8")
    print("✅ MangaDexAdapter: retry added")
else:
    print("ℹ️ MangaDexAdapter: already patched")