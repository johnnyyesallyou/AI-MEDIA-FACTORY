import sys
sys.path.insert(0, "/app")

from engines.source_adapters.remanga_adapter import ReMangaAdapter
from engines.chapter_detector import ChapterDetector

print("=" * 70)
print("DIAGNOSTICS: ReManga fetch")
print("=" * 70)

adapter = ReMangaAdapter()

# 1. Проверяем raw fetch (без ChapterDetector)
print("\n[1] Raw API fetch (без ChapterDetector)...")
try:
    url = f"{adapter.BASE_URL}/api/titles/last-chapters/"
    response = adapter._session.get(url, headers=adapter.HEADERS, timeout=15)
    data = response.json()
    raw_chapters = data.get("content", [])
    print(f"  API returned {len(raw_chapters)} chapters")
    if raw_chapters:
        print(f"  First: {raw_chapters[0].get('rus_name', 'Unknown')}")
except Exception as e:
    print(f"  ERROR: {e}")

# 2. Проверяем fetch_latest_chapters (с парсингом)
print("\n[2] fetch_latest_chapters() (с парсингом)...")
items = adapter.fetch_latest_chapters(limit=20)
print(f"  Parsed {len(items)} SourceItems")

# 3. Проверяем ChapterDetector
print("\n[3] ChapterDetector.detect_new_chapters()...")
detector = ChapterDetector()
new_items, _ = detector.detect_new_chapters(items, update_state=False)  # Не обновляем состояние
print(f"  New items (without update): {len(new_items)}")

# 4. С update_state=True
print("\n[4] ChapterDetector с update_state=True...")
new_items_with_update, _ = detector.detect_new_chapters(items, update_state=True)
print(f"  New items (with update): {len(new_items_with_update)}")

print("\n" + "=" * 70)