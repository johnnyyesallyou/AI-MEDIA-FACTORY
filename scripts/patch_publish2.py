import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
content = p.read_text(encoding="utf-8")

# ??????? fallback ?? manga_title_id (??? ?????, ?? slug)
old_slug_logic = '''            if source_url and "remanga.org" in source_url:
                try:
                    slug = metadata.get("manga_title_slug") or metadata.get("manga_title_id")
                    if not slug:
                        # ????????? slug ?? URL: https://remanga.org/manga/<slug>/<id>
                        import re
                        m = re.search(r"remanga\\.org/manga/([^/]+)/", source_url)
                        if m:
                            slug = m.group(1)'''

new_slug_logic = '''            if source_url and "remanga.org" in source_url:
                try:
                    slug = metadata.get("manga_title_slug")
                    if not slug:
                        # Fallback: ????????? slug ?? URL
                        import re
                        m = re.search(r"remanga\\.org/manga/([^/]+)/", source_url)
                        if m:
                            slug = m.group(1)'''

if old_slug_logic in content:
    content = content.replace(old_slug_logic, new_slug_logic)
    print("? Slug logic fixed (removed ID fallback)")
else:
    print("? Slug logic block not found")

p.write_text(content, encoding="utf-8")

import ast
try:
    ast.parse(content)
    print("? MangaPublishJob syntax OK")
except SyntaxError as e:
    print(f"? Syntax error: {e}")
