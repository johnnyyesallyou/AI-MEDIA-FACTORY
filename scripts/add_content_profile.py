import pathlib

p = pathlib.Path("C:/Users/Johnn/AI-MEDIA-FACTORY/core/models/channel_orm.py")
c = p.read_text(encoding="utf-8")

# 1. Проверяем наличие JSONB импорта
if "from sqlalchemy.dialects.postgresql import JSONB" not in c:
    c = c.replace(
        "from sqlalchemy import",
        "from sqlalchemy.dialects.postgresql import JSONB\nfrom sqlalchemy import",
        1
    )
    print("✅ Added JSONB import")

# 2. Добавляем колонку content_profile после sources
if "content_profile" not in c:
    marker = "    sources = Column(JSON, default=list)\n"
    if marker in c:
        new_col = "    sources = Column(JSON, default=list)\n    content_profile = Column(JSONB, nullable=True)\n"
        c = c.replace(marker, new_col, 1)
        print("✅ Added content_profile column")
    else:
        print("❌ Marker 'sources = Column' not found")
else:
    print("ℹ️ content_profile already exists")

p.write_text(c, encoding="utf-8")
print("✅ File saved")