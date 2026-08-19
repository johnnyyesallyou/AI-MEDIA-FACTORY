import asyncio
import sys
sys.path.insert(0, '/app')

async def test():
    print("🚀 Importing automation_scheduler...")
    from backend.automation.scheduler import automation_scheduler
    
    print("🚀 Starting scheduler...")
    await automation_scheduler.start()
    
    print("📋 Getting jobs...")
    jobs = automation_scheduler.scheduler.get_jobs()
    print(f"✅ Total jobs registered: {len(jobs)}")
    for job in jobs:
        print(f"   - {job.id}: {job.name}")
    
    print("🛑 Stopping scheduler...")
    await automation_scheduler.stop()

asyncio.run(test())
