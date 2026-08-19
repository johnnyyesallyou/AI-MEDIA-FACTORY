import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_research_job.py")
content = p.read_text(encoding="utf-8")

# ????????? manga_title_slug ? metadata ??? ???????? research item
old_metadata = '''        manga_metadata = {
            "type": "manga_chapter",
            "manga_source": item.source,
            "manga_title_id": item.title_id,
            "manga_title_name": item.title_name,
            "manga_title_name_en": item.title_name_en,
            "manga_chapter_number": item.chapter_number,
            "manga_chapter_id": item.chapter_id,
            "manga_cover_url": item.cover_url,
            "manga_title_url": item.title_url,
            "manga_chapter_url": item.chapter_url,
            "manga_upload_date": item.upload_date.isoformat() if item.upload_date else None,
        }'''

new_metadata = '''        manga_metadata = {
            "type": "manga_chapter",
            "manga_source": item.source,
            "manga_title_id": item.title_id,
            "manga_title_slug": item.title_slug,
            "manga_title_name": item.title_name,
            "manga_title_name_en": item.title_name_en,
            "manga_chapter_number": item.chapter_number,
            "manga_chapter_id": item.chapter_id,
            "manga_cover_url": item.cover_url,
            "manga_title_url": item.title_url,
            "manga_chapter_url": item.chapter_url,
            "manga_upload_date": item.upload_date.isoformat() if item.upload_date else None,
        }'''

if old_metadata in content:
    content = content.replace(old_metadata, new_metadata)
    print("? manga_title_slug added to metadata")
else:
    print("? Metadata block not found (may already be patched)")

p.write_text(content, encoding="utf-8")

# Syntax check
import ast
try:
    ast.parse(content)
    print("? MangaResearchJob syntax OK")
except SyntaxError as e:
    print(f"? Syntax error: {e}")
