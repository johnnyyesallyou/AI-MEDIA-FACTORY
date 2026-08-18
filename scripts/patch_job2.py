import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

# 1. Включаем MangaDex в выборку
old_q = 'ContentORM.source_url.like("%remanga.org%")\n            ).limit(limit * 2).all()'
new_q = '(ContentORM.source_url.like("%remanga.org%") | ContentORM.source_url.like("%mangadex.org%"))\n            ).limit(limit * 2).all()'
if old_q in c:
    c = c.replace(old_q, new_q)
    print("✅ Query includes MangaDex")

# 2. Используем новый preview resolver
old_prev = "preview_pages = adapter.fetch_first_chapter_preview(slug, limit=5)"
new_prev = "from engines.preview_resolver import resolve_preview_pages\n                        preview_pages = resolve_preview_pages(slug, limit=5)"
if old_prev in c:
    c = c.replace(old_prev, new_prev)
    print("✅ Preview resolver switched")

p.write_text(c, encoding="utf-8")
import ast
ast.parse(c)
print("✅ Syntax OK")