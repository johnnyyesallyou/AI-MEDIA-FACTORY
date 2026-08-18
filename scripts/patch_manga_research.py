import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_research_job.py")
c = p.read_text(encoding="utf-8")

# Ищем и заменяем старый вызов enricher
old = "sources_data = self.enricher.fetch_source_data(title)"
new = "sources_data = self.enricher._build_sources_data(title)"

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ manga_research_job.py: fetch_source_data → _build_sources_data")
else:
    print("ℹ️ Marker not found or already fixed")