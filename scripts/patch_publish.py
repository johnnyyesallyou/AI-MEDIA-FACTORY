import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
content = p.read_text(encoding="utf-8")

# 1. ????????? ?????? ReMangaAdapter
if "from engines.source_adapters.remanga_adapter import ReMangaAdapter" not in content:
    old_import = "from engines.url_shortener import URLShortener"
    new_import = old_import + "\nfrom engines.source_adapters.remanga_adapter import ReMangaAdapter"
    content = content.replace(old_import, new_import)
    print("? Added ReMangaAdapter import")

# 2. ? _publish_manga_post ????????? ?????????? preview
old_block = """            telegraph_result = telegraph.publish_manga_page(
                title=page_title,
                description=description,
                cover_url=cover_url,
                source_url=source_url,
                chapter_url=chapter_url
            )"""

new_block = """            # Sprint 18: ?????? ?????? ????? ??? ReManga
            preview_pages = None
            if source_url and "remanga.org" in source_url:
                try:
                    slug = metadata.get("manga_title_slug") or metadata.get("manga_title_id")
                    if not slug:
                        # ????????? slug ?? URL: https://remanga.org/manga/<slug>/<id>
                        import re
                        m = re.search(r"remanga\.org/manga/([^/]+)/", source_url)
                        if m:
                            slug = m.group(1)
                    
                    if slug:
                        adapter = ReMangaAdapter()
                        preview_pages = adapter.fetch_first_chapter_preview(slug, limit=5)
                        if preview_pages:
                            self.logger.info(f"Got {len(preview_pages)} preview pages for {slug}")
                except Exception as e:
                    self.logger.warning(f"Preview fetch failed: {e}")
            
            telegraph_result = telegraph.publish_manga_page(
                title=page_title,
                description=description,
                cover_url=cover_url,
                source_url=source_url,
                chapter_url=chapter_url,
                preview_pages=preview_pages
            )"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("? Added preview_pages logic")
else:
    print("? Block not found")

p.write_text(content, encoding="utf-8")

# ????????? ?????????
import ast
try:
    ast.parse(content)
    print("? Syntax OK")
except SyntaxError as e:
    print(f"? Syntax error: {e}")
