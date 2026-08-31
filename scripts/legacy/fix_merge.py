import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_research_job.py")
c = p.read_text(encoding="utf-8")

# Ищем точную строку 159
old_line = "                desc, genres, cover = self.enricher.merge(sources_data)"
new_lines = """                # Sprint 51: используем enrich() вместо merge() (merge внутри enrich)
                self.enricher.enrich(title)
                desc = title.description
                genres = title.genres
                cover = title.cover_url"""

if old_line in c:
    c = c.replace(old_line, new_lines, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] FIX 1 applied: .merge() → .enrich()")
else:
    print("[!] Line not found")
    # Ищем похожие паттерны
    for i, line in enumerate(c.split('\n'), 1):
        if 'merge' in line and 'enricher' in line:
            print(f"  Line {i}: {line}")