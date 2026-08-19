import pathlib

p = pathlib.Path("/app/engines/manga_knowledge_engine.py")
c = p.read_text(encoding="utf-8")

# Меняем _update_external_ids: используем title_external_id, а не external_id (это ID главы)
old = '''    def _update_external_ids(self, title: MangaTitle, item: MangaItem):
        if not item.external_id:
            return
        external_ids = dict(title.external_ids or {})
        if item.source not in external_ids:
            external_ids[item.source] = item.external_id
            title.external_ids = external_ids'''

new = '''    def _update_external_ids(self, title: MangaTitle, item: MangaItem):
        """Сохраняет ID тайтла из источника (не главы!)."""
        title_id = item.title_external_id
        if not title_id:
            return
        external_ids = dict(title.external_ids or {})
        if item.source not in external_ids:
            external_ids[item.source] = title_id
            title.external_ids = external_ids'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ MangaKnowledgeEngine: uses title_external_id")
else:
    print("❌ Marker not found")