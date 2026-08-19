import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from backend.automation.jobs.manga_research_job import MangaResearchJob

print("=" * 70)
print("TESTING MangaResearchJob")
print("=" * 70)

# Check initial state (using status=research filter only)
db = SessionLocal()
initial_research = db.query(ContentORM).filter(
    ContentORM.status == "research"
).count()
print(f"\n[1] Initial research items (status=research): {initial_research}")
db.close()

# Run job (first time)
print("\n[2] Running MangaResearchJob (first run)...")
job = MangaResearchJob()
result1 = job.run(limit_per_source=10)
print(f"  Result: {result1}")

# Check state after first run
db = SessionLocal()
research_after_1 = db.query(ContentORM).filter(
    ContentORM.status == "research"
).count()
print(f"\n[3] Research items after first run: {research_after_1}")

# Show created items
items = db.query(ContentORM).filter(
    ContentORM.status == "research"
).order_by(ContentORM.created_at.desc()).limit(3).all()

print("\n[4] First 3 created research items:")
for i, item in enumerate(items, 1):
    print(f"\n  Item {i}:")
    print(f"    Headline: {item.headline}")
    print(f"    Status: {item.status}")
    print(f"    Source URL: {item.source_url}")
    print(f"    Draft text preview: {item.draft_text[:100]}...")
    if item.source_text:
        print(f"    Source text preview: {item.source_text[:150]}...")
db.close()

# Run job again (should NOT create new items - deduplication)
print("\n[5] Running MangaResearchJob (second run)...")
result2 = job.run(limit_per_source=10)
print(f"  Result: {result2}")

# Check state after second run
db = SessionLocal()
research_after_2 = db.query(ContentORM).filter(
    ContentORM.status == "research"
).count()
print(f"\n[6] Research items after second run: {research_after_2}")
db.close()

# Verify
print("\n" + "=" * 70)
if result1['research_items_created'] > 0 and result2['research_items_created'] == 0:
    print("TEST PASSED")
    print(f"  First run: created {result1['research_items_created']} research items")
    print(f"  Second run: created {result2['research_items_created']} items (deduplication works)")
else:
    print("TEST FAILED")
print("=" * 70)
