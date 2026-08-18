import sys
sys.path.insert(0, "/app")

from engines.source_adapters import ReMangaAdapter
from engines.chapter_detector import ChapterDetector

print("=" * 70)
print("TESTING ChapterDetector")
print("=" * 70)

# Step 1: Fetch chapters
print("\n[1] Fetching latest chapters from ReManga...")
adapter = ReMangaAdapter()
items = adapter.fetch_latest_chapters(limit=5)
print(f"  Fetched {len(items)} chapters")

# Step 2: First run - all should be NEW
print("\n[2] First run: detecting new chapters...")
detector = ChapterDetector()
new_items, existing_items = detector.detect_new_chapters(items, update_state=True)

print(f"  New chapters: {len(new_items)}")
print(f"  Existing chapters: {len(existing_items)}")

if new_items:
    print("\n  New chapters:")
    for item in new_items[:3]:
        print(f"    - {item.title_name} chapter {item.chapter_number}")

# Step 3: Second run - all should be EXISTING (no new chapters)
print("\n[3] Second run: detecting new chapters again...")
new_items_2, existing_items_2 = detector.detect_new_chapters(items, update_state=True)

print(f"  New chapters: {len(new_items_2)}")
print(f"  Existing chapters: {len(existing_items_2)}")

# Step 4: Verify state in DB
print("\n[4] Checking manga_source_states in DB...")
from core.database import SessionLocal
from core.models.manga_source_state_orm import MangaSourceStateORM

db = SessionLocal()
states = db.query(MangaSourceStateORM).filter(
    MangaSourceStateORM.source == "remanga"
).all()
print(f"  Total states: {len(states)}")

for state in states[:3]:
    print(f"    - {state.title_name}: chapter {state.last_chapter_number}")
db.close()

print("\n" + "=" * 70)
if len(new_items) > 0 and len(new_items_2) == 0:
    print("TEST PASSED: ChapterDetector works correctly")
    print("  First run: detected new chapters")
    print("  Second run: no new chapters (deduplication works)")
else:
    print("TEST FAILED: ChapterDetector issue")
print("=" * 70)
