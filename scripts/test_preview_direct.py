import sys, re, json
sys.path.insert(0, '/app')
from engines.preview_resolver import resolve_preview_pages
from core.database import SessionLocal
from core.models.content_orm import ContentORM

db = SessionLocal()
items = db.query(ContentORM).filter(
    ContentORM.telegraph_url != None,
    ContentORM.source_url.like("%remanga.org%")
).order_by(ContentORM.updated_at.desc()).limit(3).all()

for item in items:
    meta = json.loads(item.source_text or '{}')
    chapter_url = meta.get('manga_chapter_url') or item.source_url
    print(f'\n=== {item.headline[:60]} ===')
    print(f'Chapter URL: {chapter_url}')
    
    # Извлекаем slug
    m = re.search(r'remanga\.org/manga/([^/]+)', chapter_url)
    if m:
        slug = m.group(1)
        print(f'Extracted slug: {slug}')
        pages = resolve_preview_pages(slug, limit=5)
        print(f'Preview pages type: {type(pages).__name__}')
        print(f'Preview pages: {pages}')
        if pages:
            print(f'Count: {len(pages)}')
            for i, p in enumerate(pages, 1):
                print(f'  {i}. {p[:100]}')
    else:
        print('Could not extract slug')

db.close()