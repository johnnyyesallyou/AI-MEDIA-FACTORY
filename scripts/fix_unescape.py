import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

changed = False

# 1. Unescape description в _build_publication
old1 = '''        description = manga_title.description or ""'''
new1 = '''        description = html_lib.unescape(manga_title.description or "")'''
if old1 in c:
    c = c.replace(old1, new1, 1)
    changed = True

# 2. Unescape description для Telegraph
old2 = '''                    description=manga_title.description or "",'''
new2 = '''                    description=html_lib.unescape(manga_title.description or ""),'''
if old2 in c:
    c = c.replace(old2, new2, 1)
    changed = True

if changed:
    p.write_text(c, encoding="utf-8")
    print("✅ description unescape fixed")
else:
    print("ℹ️ Markers not found")