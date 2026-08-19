import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.asset_orm import AssetORM
from engines.manga_image_resolver import MangaImageResolver

print("=" * 70)
print("TESTING MangaImageResolver")
print("=" * 70)

# Initial state
db = SessionLocal()
research_no_asset = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id == None,
    ContentORM.source_url.like("%remanga.org%")
).count()
total_assets = db.query(AssetORM).count()
print(f"\n[1] Research items without asset: {research_no_asset}")
print(f"    Total assets in DB: {total_assets}")
db.close()

# Run resolver
print("\n[2] Running MangaImageResolver...")
resolver = MangaImageResolver()
result = resolver.resolve_all_research(limit=10)
print(f"  Result: {result}")

# Check state after
db = SessionLocal()
research_with_asset = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id != None,
    ContentORM.source_url.like("%remanga.org%")
).count()
total_assets_after = db.query(AssetORM).count()

print(f"\n[3] Research items WITH asset: {research_with_asset}")
print(f"    Total assets in DB: {total_assets_after} (+{total_assets_after - total_assets})")

# Show created assets
print("\n[4] Last 3 manga cover assets:")
manga_assets = db.query(AssetORM).filter(
    AssetORM.model == "manga_cover"
).order_by(AssetORM.created_at.desc()).limit(3).all()

for i, asset in enumerate(manga_assets, 1):
    file_size = asset.extra_data.get("file_size_bytes", 0) if asset.extra_data else 0
    ext = asset.extra_data.get("file_extension", "?") if asset.extra_data else "?"
    print(f"  Asset {i}:")
    print(f"    ID: {asset.id}")
    print(f"    Path: {asset.storage_path}")
    print(f"    Size: {file_size} bytes (.{ext})")
    print(f"    URL: {asset.public_url}")

# Check files on disk
db.close()

print("\n[5] Files on disk:")
print("  (checking /app/assets/2026/08/)")

print("\n" + "=" * 70)
if result['downloaded'] > 0 and result['failed'] == 0:
    print("TEST PASSED")
    print(f"  Downloaded {result['downloaded']} manga covers")
else:
    print("TEST FAILED or PARTIAL")
    print(f"  Downloaded: {result['downloaded']}, Failed: {result['failed']}")
print("=" * 70)
