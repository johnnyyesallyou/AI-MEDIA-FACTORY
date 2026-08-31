import sys
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM

db = SessionLocal()
need = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id == None
).count()
print(f"Items without covers: {need}")
db.close()

from engines.manga_image_resolver import MangaImageResolver
resolver = MangaImageResolver()
for meth in ["run", "resolve_all", "process"]:
    if hasattr(resolver, meth):
        print(f"Calling {meth}()...")
        print(getattr(resolver, meth)())
        break