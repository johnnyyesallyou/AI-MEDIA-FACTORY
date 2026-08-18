import sys, json, requests
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("FIX: Unknown titles")
print("=" * 70)

db = SessionLocal()
items = db.query(ContentORM).filter(
    ContentORM.headline.like("%Unknown%")
).all()

print(f"Items to fix: {len(items)}")

UA = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
fixed = 0

for it in items:
    meta = json.loads(it.source_text)
    manga_id = meta.get("manga_title_id")
    
    if not manga_id:
        continue
    
    try:
        r = requests.get(
            f"https://api.mangadex.org/manga/{manga_id}",
            headers=UA,
            timeout=10
        )
        
        if r.status_code == 200:
            data = r.json().get("data", {})
            attrs = data.get("attributes", {})
            titles = attrs.get("title", {})
            
            # Пробуем разные языки
            title = (
                titles.get("ru") or 
                titles.get("en") or 
                titles.get("ja") or
                list(titles.values())[0] if titles else None
            )
            
            if title:
                # Обновляем headline
                chapter_num = meta.get("manga_chapter_number", "?")
                new_headline = f"\U0001f4da \u041d\u043e\u0432\u0430\u044f \u0433\u043b\u0430\u0432\u0430: {title} \u2014 \u0433\u043b\u0430\u0432\u0430 {chapter_num}"
                it.headline = new_headline
                
                # Обновляем metadata
                meta["manga_title_name"] = title
                it.source_text = json.dumps(meta, ensure_ascii=False)
                
                fixed += 1
                print(f"  ✅ {it.headline[:60]}")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

db.commit()
print(f"\n✅ Fixed: {fixed} items")
db.close()
print("=" * 70)