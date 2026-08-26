import sys, requests
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM

db = SessionLocal()

# Все опубликованные за последний час
from datetime import datetime, timedelta
recent_cutoff = datetime.utcnow() - timedelta(hours=24)
items = db.query(ContentORM).filter(
    ContentORM.status == "published",
    ContentORM.updated_at >= recent_cutoff
).order_by(ContentORM.updated_at.desc()).limit(5).all()

print(f"Recent published items: {len(items)}\n")
for item in items:
    print(f"Headline: {item.headline[:70]}")
    print(f"  telegraph_url: {item.telegraph_url or 'NONE'}")
    print(f"  image_url: {(item.image_url or 'NONE')[:80]}")
    
    if item.telegraph_url:
        try:
            path = item.telegraph_url.replace("https://telegra.ph/", "")
            api_url = f"https://api.telegra.ph/getPage/{path}?return_content=true"
            resp = requests.get(api_url, timeout=10)
            data = resp.json()
            if data.get("ok"):
                content = data.get("result", {}).get("content", [])
                img_count = sum(1 for n in content if n.get("tag") == "img")
                print(f"  Telegraph content: {len(content)} nodes, {img_count} images")
            else:
                print(f"  Telegraph API error: {data.get('error')}")
        except Exception as e:
            print(f"  Telegraph fetch failed: {e}")
    print()

db.close()