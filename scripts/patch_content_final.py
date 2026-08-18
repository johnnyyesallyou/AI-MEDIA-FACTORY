import pathlib

p = pathlib.Path("C:/Users/Johnn/AI-MEDIA-FACTORY/core/models/content_orm.py")
c = p.read_text(encoding="utf-8")

if "manga_chapter_id" not in c:
    # Ищем последний Column(...) перед created_at
    marker = "    created_at = Column(DateTime, default=datetime.utcnow)"
    new_field = "    manga_chapter_id = Column(String, nullable=True, index=True)\n    created_at = Column(DateTime, default=datetime.utcnow)"
    if marker in c:
        c = c.replace(marker, new_field, 1)
        p.write_text(c, encoding="utf-8")
        print("✅ manga_chapter_id added before created_at")
    else:
        # Попробуем другой marker
        marker2 = "    created_at ="
        idx = c.find(marker2)
        if idx > 0:
            c = c[:idx] + "    manga_chapter_id = Column(String, nullable=True, index=True)\n" + c[idx:]
            p.write_text(c, encoding="utf-8")
            print("✅ manga_chapter_id added (fallback)")
        else:
            print("❌ Could not find insertion point")
else:
    print("ℹ️ Field already exists")