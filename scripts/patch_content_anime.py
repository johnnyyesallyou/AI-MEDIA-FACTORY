import pathlib

p = pathlib.Path("/app/core/models/content_orm.py")
c = p.read_text(encoding="utf-8")

if "anime_episode_id" not in c:
    marker = "    manga_chapter_id = Column(String, nullable=True, index=True)"
    new_field = "    manga_chapter_id = Column(String, nullable=True, index=True)\n    anime_episode_id = Column(String, nullable=True, index=True)"
    if marker in c:
        c = c.replace(marker, new_field, 1)
        p.write_text(c, encoding="utf-8")
        print("✅ anime_episode_id added to ContentORM")
    else:
        print("❌ Marker not found")
else:
    print("ℹ️ Field already exists")