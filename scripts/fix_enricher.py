import pathlib

p = pathlib.Path("/app/engines/cross_source_enricher.py")
c = p.read_text(encoding="utf-8")

# Ищем вызовы fetch_source_data
import re

# Паттерн: self.fetch_source_data(...)
matches = list(re.finditer(r'self\.fetch_source_data\(', c))

if not matches:
    print("✅ No old fetch_source_data calls found")
else:
    print(f"Found {len(matches)} calls to fetch_source_data:")
    for m in matches:
        start = max(0, m.start() - 50)
        end = min(len(c), m.end() + 50)
        print(f"  ...{c[start:end]}...")
    
    # Нужно заменить на новый API
    # self.fetch_source_data(...) → self._enrich_from_source(...)
    # Но это сложно без контекста
    
    print("\n⚠️ Manual fix needed - showing context")