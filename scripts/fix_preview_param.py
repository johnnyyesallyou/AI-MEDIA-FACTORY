import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

# Ищем вызов publish_manga_page и добавляем preview_pages параметр
old_call = '''                result = telegraph.publish_manga_page(
                    title=f"{title_name} — глава {chapter_number}",
                    description=html_lib.unescape(manga_title.description or ""),
                    cover_url=cover_url,
                    source_url=item.source_url,
                    chapter_url=chapter_url,'''

new_call = '''                result = telegraph.publish_manga_page(
                    title=f"{title_name} — глава {chapter_number}",
                    description=html_lib.unescape(manga_title.description or ""),
                    cover_url=cover_url,
                    source_url=item.source_url,
                    chapter_url=chapter_url,
                    preview_pages=preview_pages,  # Sprint 51: превью страниц'''

if old_call in c and "preview_pages=preview_pages" not in c:
    c = c.replace(old_call, new_call, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] preview_pages параметр добавлен в publish_manga_page")
else:
    print("[i] Уже добавлено или паттерн не найден")