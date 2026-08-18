import pathlib

p = pathlib.Path("/app/engines/source_adapters/remanga_adapter.py")
c = p.read_text(encoding="utf-8")

# В _to_manga_item добавить title_external_id
old = '''            external_id=item.chapter_id or item.title_id,'''
new = '''            external_id=item.chapter_id or item.title_id,
            title_external_id=item.title_id,'''

if old in c and "title_external_id=item.title_id" not in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ ReMangaAdapter: title_external_id added")
else:
    print("ℹ️ Already patched or marker not found")