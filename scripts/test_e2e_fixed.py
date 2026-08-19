"""End-to-End test: Research → Writing → Image → Publish."""
import sys
import json
import asyncio
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.asset_orm import AssetORM
from core.models.channel_orm import ChannelORM

def get_initial_state():
    """Get initial state of DB."""
    db = SessionLocal()
    try:
        total_content = db.query(ContentORM).count()
        approved = db.query(ContentORM).filter(ContentORM.status == "approved").count()
        published = db.query(ContentORM).filter(ContentORM.status == "published").count()
        with_image = db.query(ContentORM).filter(ContentORM.image_url != None).count()
        total_assets = db.query(AssetORM).count()
        
        return {
            "total_content": total_content,
            "approved": approved,
            "published": published,
            "with_image": with_image,
            "total_assets": total_assets
        }
    finally:
        db.close()

def main():
    print("\n" + "="*70)
    print("END-TO-END TEST: Research → Writing → Image → Publish")
    print("="*70)
    
    # Initial state
    print("\n[INITIAL STATE]")
    state_before = get_initial_state()
    for key, value in state_before.items():
        print(f"  {key}: {value}")
    
    # Step 1: Research
    print("\n" + "="*70)
    print("STEP 1: Research")
    print("="*70)
    
    try:
        from backend.automation.jobs.automation_jobs import ResearchJob
        db = SessionLocal()
        channel = db.query(ChannelORM).filter(ChannelORM.is_active == True).first()
        db.close()
        
        if channel:
            research_job = ResearchJob()
            result = research_job.run(channel=channel, execution_id="e2e_test_research")
            print(f"ResearchJob result: {json.dumps(result, indent=2)}")
        else:
            print("⚠️ No active channels found")
    except Exception as e:
        print(f"❌ ResearchJob failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 2: Writing
    print("\n" + "="*70)
    print("STEP 2: Writing")
    print("="*70)
    
    try:
        from backend.automation.jobs.automation_jobs import WritingJob
        db = SessionLocal()
        channel = db.query(ChannelORM).filter(ChannelORM.is_active == True).first()
        db.close()
        
        if channel:
            writing_job = WritingJob()
            result = asyncio.run(writing_job.run(channel=channel, execution_id="e2e_test_writing"))
            print(f"WritingJob result: {json.dumps(result, indent=2)}")
        else:
            print("⚠️ No active channels found")
    except Exception as e:
        print(f"❌ WritingJob failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Image (ImageJob)
    print("\n" + "="*70)
    print("STEP 3: Image Generation")
    print("="*70)
    
    try:
        from backend.automation.jobs.image_job import ImageJob
        image_job = ImageJob()
        result = image_job.run(limit=3)
        print(f"ImageJob result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ ImageJob failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Publish
    print("\n" + "="*70)
    print("STEP 4: Publishing")
    print("="*70)
    
    try:
        from backend.automation.jobs.automation_jobs import PublishJob
        db = SessionLocal()
        channel = db.query(ChannelORM).filter(ChannelORM.is_active == True).first()
        db.close()
        
        if channel:
            publish_job = PublishJob()
            result = publish_job.run(channel=channel, execution_id="e2e_test_publish")
            print(f"PublishJob result: {json.dumps(result, indent=2)}")
        else:
            print("⚠️ No active channels found")
    except Exception as e:
        print(f"❌ PublishJob failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Final state
    print("\n" + "="*70)
    print("FINAL STATE")
    print("="*70)
    state_after = get_initial_state()
    for key, value in state_after.items():
        delta = value - state_before[key]
        delta_str = f" (+{delta})" if delta > 0 else f" ({delta})" if delta < 0 else ""
        print(f"  {key}: {value}{delta_str}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Content created: {state_after['total_content'] - state_before['total_content']}")
    print(f"Approved: {state_after['approved'] - state_before['approved']}")
    print(f"Published: {state_after['published'] - state_before['published']}")
    print(f"Images generated: {state_after['with_image'] - state_before['with_image']}")
    print(f"Assets created: {state_after['total_assets'] - state_before['total_assets']}")
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)

if __name__ == "__main__":
    main()
