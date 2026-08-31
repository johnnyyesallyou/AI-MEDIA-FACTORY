import pathlib

p = pathlib.Path("/app/backend/automation/runtime/jobs_registry.py")
c = p.read_text(encoding="utf-8")

# Добавляем импорты адаптеров
if "MangaResearchJobAdapter" not in c:
    c = c.replace(
        "from backend.automation.runtime.job_adapters import (",
        "from backend.automation.runtime.job_adapters import (\n    MangaResearchJobAdapter, MangaEnrichmentJobAdapter, MangaPublishJobAdapter,\n    AnimeResearchJobAdapter, AnimePublishJobAdapter,",
    )
    
    # Переопределяем регистрацию manga/anime jobs на адаптеры
    c = c.replace(
        '    JobFactory.register("manga_research", MangaResearchJob)',
        '    JobFactory.register("manga_research", MangaResearchJobAdapter)  # Sprint 51: use adapter',
    )
    c = c.replace(
        '    JobFactory.register("manga_enrichment", MangaEnrichmentJob)',
        '    JobFactory.register("manga_enrichment", MangaEnrichmentJobAdapter)  # Sprint 51: use adapter',
    )
    c = c.replace(
        '    JobFactory.register("manga_publish", MangaPublishJob)',
        '    JobFactory.register("manga_publish", MangaPublishJobAdapter)  # Sprint 51: use adapter',
    )
    c = c.replace(
        '    JobFactory.register("anime_research", AnimeResearchJob)',
        '    JobFactory.register("anime_research", AnimeResearchJobAdapter)  # Sprint 51: use adapter',
    )
    c = c.replace(
        '    JobFactory.register("anime_publish", AnimePublishJob)',
        '    JobFactory.register("anime_publish", AnimePublishJobAdapter)  # Sprint 51: use adapter',
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] Registered manga/anime adapters")
else:
    print("[i] Already registered")