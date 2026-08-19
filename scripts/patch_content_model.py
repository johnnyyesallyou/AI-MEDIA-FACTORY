import pathlib

p = pathlib.Path("C:/Users/Johnn/AI-MEDIA-FACTORY/core/models/content_orm.py")
c = p.read_text(encoding="utf-8")

if "manga_chapter_id" not in c:
    # Добавляем поле перед updated_at
    marker = "    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)"
    new_field = "    manga_chapter_id = Column(String, nullable=True, index=True)\n    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)"
    if marker in c:
        c = c.replace(marker, new_field, 1)
        p.write_text(c, encoding="utf-8")
        print("✅ manga_chapter_id field added to ContentORM")
    else:
        print("❌ Marker not found")
else:
    print("ℹ️ Field already exists")