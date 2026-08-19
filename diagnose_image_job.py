"""Diagnostic script to understand why ImageJob processes 0 items."""
import sys
import json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.repositories.content_repository import ContentRepository

print("\n" + "="*70)
print("DIAGNOSTIC: Why ImageJob processes 0 items?")
print("="*70)

db = SessionLocal()
try:
    # Check what repo.list_all returns
    repo = ContentRepository(db)
    
    print("\n[1] Testing repo.list_all(status='approved', limit=3):")
    items = repo.list_all(status="approved", limit=3)
    print(f"    Returned {len(items)} items")
    
    for i, item in enumerate(items, 1):
        has_image = getattr(item, 'image_url', None) is not None
        print(f"    {i}. {item.id[:8]}... | status={item.status} | image_url={'YES' if has_image else 'NO'}")
        if has_image:
            print(f"       URL: {item.image_url[:80]}...")
    
    # Filter like ImageJob does
    filtered = [i for i in items if not getattr(i, 'image_url', None)]
    print(f"\n[2] After filtering (no image_url): {len(filtered)} items")
    
    # Check direct DB query
    print("\n[3] Direct DB query (approved without image_url, limit=3):")
    direct_items = db.query(ContentORM).filter(
        ContentORM.status == "approved",
        ContentORM.image_url == None
    ).limit(3).all()
    
    print(f"    Returned {len(direct_items)} items")
    for i, item in enumerate(direct_items, 1):
        print(f"    {i}. {item.id[:8]}... | {item.headline[:50]}...")
    
    # Check total counts
    print("\n[4] Total counts:")
    total_approved = db.query(ContentORM).filter(ContentORM.status == "approved").count()
    total_with_image = db.query(ContentORM).filter(
        ContentORM.status == "approved",
        ContentORM.image_url != None
    ).count()
    total_without_image = db.query(ContentORM).filter(
        ContentORM.status == "approved",
        ContentORM.image_url == None
    ).count()
    
    print(f"    Total approved: {total_approved}")
    print(f"    Approved WITH image_url: {total_with_image}")
    print(f"    Approved WITHOUT image_url: {total_without_image}")
    
    # Check what repo.list_all actually does
    print("\n[5] Checking repo.list_all implementation:")
    import inspect
    source = inspect.getsource(repo.list_all)
    print(source[:500])
    
finally:
    db.close()

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETED")
print("="*70)
