import pathlib
p = pathlib.Path("/app/backend/automation/runtime/jobs_registry.py")
c = p.read_text(encoding="utf-8")

# Проверяем что все адаптеры импортируются из job_adapters
needed = [
    "MangaResearchJobAdapter",
    "MangaEnrichmentJobAdapter", 
    "MangaPublishJobAdapter",
    "AnimeResearchJobAdapter",
    "AnimePublishJobAdapter",
]

# Убеждаемся что import блок правильный
if "from backend.automation.runtime.job_adapters import (" in c:
    # Проверяем что все адаптеры в import блоке
    for adapter in needed:
        if adapter not in c:
            print(f"[!] Missing import: {adapter}")
            # Добавляем в существующий import блок
            c = c.replace(
                "from backend.automation.runtime.job_adapters import (",
                f"from backend.automation.runtime.job_adapters import (\n    {adapter},",
            )
            print(f"[OK] Added {adapter} to imports")
    
    # Проверяем что регистрация использует адаптеры
    replacements = {
        'JobFactory.register("manga_research", MangaResearchJob)': 'JobFactory.register("manga_research", MangaResearchJobAdapter)',
        'JobFactory.register("manga_enrichment", MangaEnrichmentJob)': 'JobFactory.register("manga_enrichment", MangaEnrichmentJobAdapter)',
        'JobFactory.register("manga_publish", MangaPublishJob)': 'JobFactory.register("manga_publish", MangaPublishJobAdapter)',
        'JobFactory.register("anime_research", AnimeResearchJob)': 'JobFactory.register("anime_research", AnimeResearchJobAdapter)',
        'JobFactory.register("anime_publish", AnimePublishJob)': 'JobFactory.register("anime_publish", AnimePublishJobAdapter)',
    }
    
    for old, new in replacements.items():
        if old in c:
            c = c.replace(old, new, 1)
            print(f"[OK] {old} -> {new}")
    
    p.write_text(c, encoding="utf-8")
    print("[OK] jobs_registry.py updated")