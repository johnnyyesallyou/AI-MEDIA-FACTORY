"""Test script for ImageJob with AssetManager integration."""
import sys
import json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.repositories.content_repository import ContentRepository
from backend.automation.jobs.image_job import ImageJob

def check_before():
    """Check state before running ImageJob."""
    db = SessionLocal()
    try:
        # Count assets
        assets_count = db.query(ContentORM).filter(
            ContentORM.status == "approved",
            ContentORM.image_url == None
        ).count()
        
        print(f"\n{'='*70}")
        print("BEFORE ImageJob")
        print(f"{'='*70}")
        print(f"Approved without image_url: {assets_count}")
        
        # Show first 3
        items = db.query(ContentORM).filter(
            ContentORM.status == "approved",
            ContentORM.image_url == None
        ).limit(3).all()
        
        for item in items:
            print(f"  - {item.id[:8]}... | {item.headline[:50]}...")
        
        return assets_count
    finally:
        db.close()

def check_after():
    """Check state after running ImageJob."""
    db = SessionLocal()
    try:
        # Count assets in assets table
        from core.models.asset_orm import AssetORM
        assets_count = db.query(AssetORM).count()
        
        # Count content with asset_id
        content_with_asset = db.query(ContentORM).filter(
            ContentORM.asset_id != None
        ).count()
        
        # Count content with image_url
        content_with_image = db.query(ContentORM).filter(
            ContentORM.image_url != None
        ).count()
        
        # Count content with local image_url (/assets/...)
        content_with_local = db.query(ContentORM).filter(
            ContentORM.image_url.like("/assets/%")
        ).count()
        
        print(f"\n{'='*70}")
        print("AFTER ImageJob")
        print(f"{'='*70}")
        print(f"Total assets in DB: {assets_count}")
        print(f"Content with asset_id: {content_with_asset}")
        print(f"Content with image_url: {content_with_image}")
        print(f"Content with local URL (/assets/...): {content_with_local}")
        
        # Show last 3 assets
        last_assets = db.query(AssetORM).order_by(
            AssetORM.created_at.desc()
        ).limit(3).all()
        
        if last_assets:
            print(f"\nLast 3 assets:")
            for asset in last_assets:
                print(f"  - {asset.id[:8]}... | {asset.storage_path} | {asset.public_url}")
        
        # Show last 3 content with images
        last_content = db.query(ContentORM).filter(
            ContentORM.image_url != None
        ).order_by(ContentORM.updated_at.desc()).limit(3).all()
        
        if last_content:
            print(f"\nLast 3 content with images:")
            for content in last_content:
                asset_info = f"asset_id={content.asset_id[:8] if content.asset_id else 'None'}"
                url_info = f"image_url={content.image_url[:60] if content.image_url else 'None'}..."
                print(f"  - {content.id[:8]}... | {asset_info} | {url_info}")
        
    finally:
        db.close()

def main():
    """Main test function."""
    print("\n" + "="*70)
    print("TESTING ImageJob with AssetManager Integration")
    print("="*70)
    
    # Check before
    before_count = check_before()
    
    if before_count == 0:
        print("\n⚠️ No approved content without image_url found.")
        print("Creating test content...")
        
        # Create test content
        db = SessionLocal()
        try:
            from core.models.channel_orm import ChannelORM
            
            # Get or create test channel
            channel = db.query(ChannelORM).first()
            if not channel:
                print("❌ No channels found. Cannot create test content.")
                return
            
            test_content = ContentORM(
                headline="Test Headline for Sprint 13.1",
                draft_text="This is a test post to verify AssetManager integration in ImageJob.",
                status="approved",
                channel_id=channel.id,
                quality_score=85
            )
            db.add(test_content)
            db.commit()
            print(f"✅ Created test content: {test_content.id}")
        finally:
            db.close()
    
    # Run ImageJob
    print(f"\n{'='*70}")
    print("RUNNING ImageJob")
    print(f"{'='*70}")
    
    job = ImageJob()
    result = job.run()
    
    print(f"\nImageJob result:")
    print(json.dumps(result, indent=2))
    
    # Check after
    check_after()
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)

if __name__ == "__main__":
    main()
