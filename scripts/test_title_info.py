import sys
sys.path.insert(0, "/app")

from engines.source_adapters.readmanga_adapter import ReadMangaAdapter

print("=" * 70)
print("TEST: ReadMangaAdapter.get_title_info()")
print("=" * 70)

adapter = ReadMangaAdapter()

# Тестируем с реальным slug из БД
test_slugs = ["34223", "progulka_v_drugom_mire"]

for slug in test_slugs:
    print(f"\nSlug: {slug}")
    info = adapter.get_title_info(slug)
    if info:
        print(f"  Title: {info['title'][:60]}")
        print(f"  Description: {info['description'][:80] if info['description'] else 'None'}...")
        print(f"  Genres: {info['genres'][:5]}")
        print(f"  Cover: {(info['cover_url'] or 'None')[:70]}")
    else:
        print(f"  ❌ Failed to get info")

print("\n" + "=" * 70)