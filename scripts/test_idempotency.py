"""Idempotency test for ImageJob."""
import sys
import json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.asset_orm import AssetORM
from backend.automation.jobs.image_job import ImageJob

def get_state():
    """Get current state of DB."""
    db = SessionLocal()
    try:
        total_assets = db.query(AssetORM).count()
        content_with_asset = db.query(ContentORM).filter(
            ContentORM.asset_id != None
        ).count()
        content_with_image = db.query(ContentORM).filter(
            ContentORM.image_url != None
        ).count()
        approved_without_image = db.query(ContentORM).filter(
            ContentORM.status == "approved",
            ContentORM.image_url == None
        ).count()
        
        # Check for duplicate assets (same content_id multiple times)
        duplicates = db.query(AssetORM.content_id).group_by(
            AssetORM.content_id
        ).having(
            db.query(AssetORM.content_id).count() > 1
        ).count()
        
        return {
            "total_assets": total_assets,
            "content_with_asset": content_with_asset,
            "content_with_image": content_with_image,
            "approved_without_image": approved_without_image,
            "duplicate_assets": duplicates
        }
    finally:
        db.close()

def main():
    print("\n" + "="*70)
    print("IDEMPOTENCY TEST: Run ImageJob 3 times")
    print("="*70)
    
    # Initial state
    print("\n[INITIAL STATE]")
    state_before = get_state()
    for key, value in state_before.items():
        print(f"  {key}: {value}")
    
    # Run ImageJob 3 times
    results = []
    for run_number in range(1, 4):
        print(f"\n{'='*70}")
        print(f"RUN {run_number}/3")
        print(f"{'='*70}")
        
        job = ImageJob()
        result = job.run(limit=5)
        results.append(result)
        
        print(f"Result: processed={result['processed']}, "
              f"generated={result['generated']}, "
              f"assets_created={result['assets_created']}")
    
    # Final state
    print(f"\n{'='*70}")
    print("FINAL STATE")
    print(f"{'='*70}")
    state_after = get_state()
    for key, value in state_after.items():
        delta = value - state_before[key]
        delta_str = f" (+{delta})" if delta > 0 else f" ({delta})" if delta < 0 else ""
        print(f"  {key}: {value}{delta_str}")
    
    # Analysis
    print(f"\n{'='*70}")
    print("IDEMPOTENCY ANALYSIS")
    print(f"{'='*70}")
    
    # Check if second and third runs created assets
    run1_assets = results[0]['assets_created']
    run2_assets = results[1]['assets_created']
    run3_assets = results[2]['assets_created']
    
    print(f"\nAssets created per run:")
    print(f"  Run 1: {run1_assets}")
    print(f"  Run 2: {run2_assets}")
    print(f"  Run 3: {run3_assets}")
    
    if run2_assets == 0 and run3_assets == 0:
        print("\n✅ PASS: Second and third runs did NOT create new assets")
        print("   Idempotency confirmed!")
    elif run1_assets == 0:
        print("\n⚠️ WARNING: First run did NOT create assets")
        print("   This means all posts already have images")
        if run2_assets == 0 and run3_assets == 0:
            print("   Idempotency still confirmed (no new assets in any run)")
        else:
            print("❌ FAIL: Subsequent runs created assets unexpectedly")
    else:
        print("\n❌ FAIL: Subsequent runs created new assets")
        print("   Idempotency BROKEN!")
    
    # Check for duplicates
    if state_after['duplicate_assets'] == 0:
        print("\n✅ PASS: No duplicate assets found")
    else:
        print(f"\n❌ FAIL: Found {state_after['duplicate_assets']} duplicate assets")
        print("   Some content_id have multiple assets!")
    
    print(f"\n{'='*70}")
    print("TEST COMPLETED")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
