import sys, json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.manga_knowledge import MangaTitle, MangaChapter

db = SessionLocal()

print("=" * 70)
print("QUALITY CHECK: опубликованные посты")
print("=" * 70)

posts = db.query(ContentORM).filter(
    ContentORM.status == "published",
    ContentORM.manga_chapter_id != None,
).order_by(ContentORM.published_at.desc()).limit(10).all()

issues = []
for i, post in enumerate(posts, 1):
    chapter = db.query(MangaChapter).filter(
        MangaChapter.id == post.manga_chapter_id
    ).first()
    if not chapter:
        issues.append(f"[{i}] {post.headline[:50]}: ORPHAN (no MangaChapter)")
        continue
    
    title = db.query(MangaTitle).filter(
        MangaTitle.id == chapter.manga_title_id
    ).first()
    if not title:
        issues.append(f"[{i}] {post.headline[:50]}: ORPHAN (no MangaTitle)")
        continue
    
    checks = {
        "title_name": bool(title.canonical_title),
        "chapter_number": bool(chapter.chapter_number),
        "description": bool(title.description),
        "genres": bool(title.genres),
        "cover": bool(title.cover_url),
        "source": bool(chapter.url),
    }
    
    missing = [k for k, v in checks.items() if not v]
    status = "✅" if not missing else "⚠️"
    
    print(f"\n[{i}] {post.headline[:60]}")
    print(f"    {status} title={bool(title.canonical_title)}, chapter={chapter.chapter_number}, "
          f"desc={bool(title.description)}, genres={len(title.genres or [])}, cover={bool(title.cover_url)}")
    if missing:
        print(f"    Missing: {missing}")
        issues.append(f"[{i}] {post.headline[:50]}: missing {missing}")

print(f"\n{'=' * 70}")
print(f"Total checked: {len(posts)}")
print(f"Issues: {len(issues)}")
if issues:
    print("\nIssues:")
    for issue in issues:
        print(f"  {issue}")
print("=" * 70)

db.close()