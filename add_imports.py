import pathlib
p = pathlib.Path("/app/backend/automation/runtime/job_adapters.py")
c = p.read_text(encoding="utf-8")

imports_needed = [
    "from backend.automation.jobs.manga_research_job import MangaResearchJob",
    "from backend.automation.jobs.manga_enrichment_job import MangaEnrichmentJob",
    "from backend.automation.jobs.manga_publish_job import MangaPublishJob",
    "from backend.automation.jobs.anime_research_job import AnimeResearchJob",
    "from backend.automation.jobs.anime_publish_job import AnimePublishJob",
]

added = 0
for imp in imports_needed:
    if imp not in c:
        # Вставляем после последнего from backend.automation.jobs
        lines = c.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from backend.automation.jobs"):
                insert_idx = i + 1
        lines.insert(insert_idx, imp)
        c = "\n".join(lines)
        added += 1

if added:
    p.write_text(c, encoding="utf-8")
    print(f"[OK] Added {added} imports")
else:
    print("[i] All imports present")