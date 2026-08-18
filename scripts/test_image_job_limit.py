"""Test script for ImageJob with AssetManager integration (with limit)."""
import sys
import json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.asset_orm import AssetORM
from backend.automation.jobs.image_job import ImageJob

def check_before():
    """Check state before running ImageJob."""
    db = SessionLocal()
    try:
        # Count approved without image_url
        approved_no_image = db.query(ContentORM).filter(
            ContentORM.status == "approved",
            ContentORM.image_url == None
        ).count()
        
        # Count assets
        assets_count = db.query(AssetORM).count()
        
        # Count content with asset_id
        content_with_asset = db.query(ContentORM).filter(
            ContentORM.asset_id != None
        ).count()
        
        print(f"\n{'='*70}")
        print("BEFORE ImageJob")
        print(f"{'='*70}")
        print(f"Approved without image_url: {approved_no_image}")
        print(f"Total assets in DB: {assets_count}")
        print(f"Content with asset_id: {content_with_asset}")
        
        return approved_no_image, assets_count, content_with_asset
    finally:
        db.close()

def check_after():
    """Check state after running ImageJob."""
    db = SessionLocal()
    try:
        # Count approved without image_url
        approved_no_image = db.query(ContentORM).filter(
            ContentORM.status == "approved",
            ContentORM.image_url == None
        ).count()
        
        # Count assets
        assets_count = db.query(AssetORM).count()
        
        # Count content with asset_id
        content_with_asset = db.query(ContentORM).filter(
            ContentORM.asset_id != None
        ).count()
        
        # Count content with local URL
        content_with_local = db.query(ContentORM).filter(
            ContentORM.image_url.like("/assets/%")
        ).count()
        
        print(f"\n{'='*70}")
        print("AFTER ImageJob")
        print(f"{'='*70}")
        print(f"Approved without image_url: {approved_no_image}")
        print(f"Total assets in DB: {assets_count}")
        print(f"Content with asset_id: {content_with_asset}")
        print(f"Content with local URL (/assets/...): {content_with_local}")
        
        # Show last 5 assets
        last_assets = db.query(AssetORM).order_by(
            AssetORM.created_at.desc()
        ).limit(5).all()
        
        if last_assets:
            print(f"\nLast 5 assets:")
            for asset in last_assets:
                print(f"  - {asset.id[:8]}... | {asset.storage_path} | {asset.extra_data.get('file_size_bytes', 0)} bytes")
        
        # Show last 5 content with images
        last_content = db.query(ContentORM).filter(
            ContentORM.image_url != None
        ).order_by(ContentORM.updated_at.desc()).limit(5).all()
        
        if last_content:
            print(f"\nLast 5 content with images:")
            for content in last_content:
                asset_info = f"asset_id={content.asset_id[:8] if content.asset_id else 'None'}"
                url_preview = content.image_url[:60] if content.image_url else 'None'
                print(f"  - {content.id[:8]}... | {asset_info} | {url_preview}...")
        
    finally:
        db.close()

def main():
    """Main test function."""
    print("\n" + "="*70)
    print("TESTING ImageJob with AssetManager Integration (LIMIT=3)")
    print("="*70)
    
    # Check before
    before_approved, before_assets, before_content_asset = check_before()
    
    # Run ImageJob with limit=3
    print(f"\n{'='*70}")
    print("RUNNING ImageJob (limit=3)")
    print(f"{'='*70}")
    
    job = ImageJob()
    result = job.run(limit=3)  # Тестируем только 3 поста
    
    print(f"\nImageJob result:")
    print(json.dumps(result, indent=2))
    
    # Check after
    check_after()
    
    # Calculate delta
    after_approved, after_assets, after_content_asset = check_before()
    
    print(f"\n{'='*70}")
    print("DELTA (changes)")
    print(f"{'='*70}")
    print(f"Assets created: {after_assets - before_assets}")
    print(f"Content with asset_id: {after_content_asset - before_content_asset}")
    print(f"Approved without image_url: {before_approved - after_approved}")
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)

if __name__ == "__main__":
    main()
