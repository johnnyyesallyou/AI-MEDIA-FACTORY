import pathlib

p = pathlib.Path("/app/core/models/content_orm.py")
c = p.read_text(encoding="utf-8")

# Ищем где определены поля и добавляем telegraph_url после image_url
if "telegraph_url" not in c:
    c = c.replace(
        'image_url = Column(String(500), nullable=True)',
        'image_url = Column(String(500), nullable=True)\n    telegraph_url = Column(String(500), nullable=True)  # Sprint 51: Telegraph page URL',
    )
    p.write_text(c, encoding="utf-8")
    print("[OK] Added telegraph_url field to ContentORM")
else:
    print("[i] telegraph_url already exists")