import sys, re, json, logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
sys.path.insert(0, '/app')
from engines.preview_resolver import resolve_preview_pages
from core.database import SessionLocal
from core.models.content_orm import ContentORM

db = SessionLocal()
items = db.query(ContentORM).filter(
    ContentORM.telegraph_url != None,
    ContentORM.source_url.like("%remanga.org%")
).order_by(ContentORM.updated_at.desc()).limit(2).all()

for item in items:
    meta = json.loads(item.source_text or '{}')
    chapter_url = meta.get('manga_chapter_url') or item.source_url
    print(f'\n=== {item.headline[:60]} ===')
    print(f'Chapter URL: {chapter_url}')
    
    m = re.search(r'remanga\.org/manga/([^/]+)', chapter_url)
    if m:
        slug = m.group(1)
        print(f'Slug: {slug}')
        pages = resolve_preview_pages(slug, limit=5)
        print(f'\nResult: {pages}')
        if pages:
            print(f'Count: {len(pages)}')

db.close()