import sys, requests
sys.path.insert(0, "/app")

from core.database import SessionLocal
from engines.research.models.news_article import NewsArticle

UA = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}

db = SessionLocal()
articles = db.query(NewsArticle).limit(3).all()

print("=" * 70)
print("DIAGNOSTICS: og:image URLs from Habr")
print("=" * 70)

for a in articles:
    print(f"\nTitle: {a.title[:60]}")
    print(f"  og_image: {a.og_image_url}")
    
    if a.og_image_url:
        try:
            r = requests.get(a.og_image_url, headers=UA, timeout=10, stream=True)
            print(f"  Status: {r.status_code}")
            print(f"  Content-Type: {r.headers.get('content-type')}")
            print(f"  Content-Length: {r.headers.get('content-length', 'N/A')}")
            r.close()
        except Exception as e:
            print(f"  ERROR: {e}")

db.close()
print("=" * 70)