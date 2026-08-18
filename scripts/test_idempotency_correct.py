"""Correct idempotency test for ImageJob."""
import sys
import json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.asset_orm import AssetORM
from backend.automation.jobs.image_job import ImageJob

def get_post_assets(content_id):
    """Get all assets for a specific content."""
    db = SessionLocal()
    try:
        return db.query(AssetORM).filter(
            AssetORM.content_id == content_id
        ).all()
    finally:
        db.close()

def main():
    print("\n" + "="*70)
    print("CORRECT IDEMPOTENCY TEST")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Find one post without image
        post = db.query(ContentORM).filter(
            ContentORM.status == "approved",
            ContentORM.image_url == None
        ).first()
        
        if not post:
            print("⚠️ No posts without image found. Creating test post...")
            # Create test post
            from core.models.channel_orm import ChannelORM
            channel = db.query(ChannelORM).first()
            post = ContentORM(
                headline="Test Idempotency Post",
                draft_text="Test content",
                status="approved",
                channel_id=channel.id,
                quality_score=85
            )
            db.add(post)
            db.commit()
        
        content_id = post.id
        print(f"\nTest post: {content_id}")
        print(f"  Headline: {post.headline[:50]}...")
        print(f"  image_url before: {post.image_url}")
        
    finally:
        db.close()
    
    # Run ImageJob 3 times (with limit=1 to process only our post)
    print(f"\n{'='*70}")
    print("RUNNING ImageJob 3 times (limit=1)")
    print(f"{'='*70}")
    
    for run_number in range(1, 4):
        print(f"\n--- Run {run_number}/3 ---")
        
        job = ImageJob()
        result = job.run(limit=1)
        
        print(f"Result: processed={result['processed']}, "
              f"generated={result['generated']}, "
              f"assets_created={result['assets_created']}")
        
        # Check assets for this post after each run
        assets = get_post_assets(content_id)
        print(f"Assets for post {content_id[:8]}...: {len(assets)}")
    
    # Final check
    print(f"\n{'='*70}")
    print("FINAL CHECK")
    print(f"{'='*70}")
    
    assets = get_post_assets(content_id)
    print(f"\nTotal assets for post {content_id[:8]}...: {len(assets)}")
    
    if len(assets) == 1:
        print("\n✅ PASS: Only ONE asset created after 3 runs")
        print("   Idempotency CONFIRMED!")
    elif len(assets) == 0:
        print("\n⚠️ WARNING: No assets created")
        print("   Post may have been skipped or failed")
    else:
        print(f"\n❌ FAIL: {len(assets)} assets created after 3 runs")
        print("   Idempotency BROKEN!")
    
    # Check post state
    db = SessionLocal()
    try:
        post = db.query(ContentORM).filter(ContentORM.id == content_id).first()
        print(f"\nPost state after 3 runs:")
        print(f"  image_url: {post.image_url[:80] if post.image_url else 'None'}...")
        print(f"  asset_id: {post.asset_id}")
    finally:
        db.close()
    
    print(f"\n{'='*70}")
    print("TEST COMPLETED")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
