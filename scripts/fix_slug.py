import pathlib, re

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

# Ищем блок где вызывается resolve_preview_pages
old_block = '''                    try:
                        from engines.preview_resolver import resolve_preview_pages
                        preview_pages = resolve_preview_pages(manga_title.title_slug, limit=5)
                    except Exception as e:
                        self.logger.warning(f"Preview fetch failed: {e}")'''

new_block = '''                    try:
                        from engines.preview_resolver import resolve_preview_pages
                        # Sprint 51: берём slug из URL главы (title_slug может быть MangaDex UUID)
                        chapter_url_for_slug = meta.get("manga_chapter_url") or item.source_url or ""
                        url_slug = None
                        if "remanga.org" in chapter_url_for_slug:
                            m = re.search(r"remanga\.org/manga/([^/]+)", chapter_url_for_slug)
                            if m:
                                url_slug = m.group(1)
                        
                        slug_to_use = url_slug or manga_title.title_slug
                        self.logger.info(f"Preview: using slug={slug_to_use} (url_slug={url_slug}, title_slug={manga_title.title_slug})")
                        preview_pages = resolve_preview_pages(slug_to_use, limit=5)
                        self.logger.info(f"Preview pages fetched: {len(preview_pages) if preview_pages else 0}")
                    except Exception as e:
                        self.logger.warning(f"Preview fetch failed: {e}")
                        preview_pages = None'''

if old_block in c:
    c = c.replace(old_block, new_block, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] manga_publish_job: теперь берёт slug из URL главы")
else:
    print("[!] Pattern not found")