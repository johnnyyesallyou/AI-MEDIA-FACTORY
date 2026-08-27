import sys
sys.path.insert(0, '/app')
from engines.source_registry import SourceRegistry

print("=== All sources ===")
for source in SourceRegistry.list_all():
    print(f"  {source.id}: {source.name} ({', '.join(source.content_types)})")

print("\n=== Sources for manga ===")
for source in SourceRegistry.get_sources_for("manga"):
    print(f"  {source.id}: {source.capabilities}")

print("\n=== Sources for anime ===")
for source in SourceRegistry.get_sources_for("anime"):
    print(f"  {source.id}: {source.capabilities}")

print("\n=== Sources for news ===")
for source in SourceRegistry.get_sources_for("news"):
    print(f"  {source.id}: {source.capabilities}")

print("\n=== Validate sources ===")
valid, invalid = SourceRegistry.validate_sources(["remanga", "mangadex", "invalid_source"])
print(f"  Valid: {valid}")
print(f"  Invalid: {invalid}")