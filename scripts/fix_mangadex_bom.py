import pathlib

p = pathlib.Path("/app/engines/source_adapters/mangadex_adapter.py")
data = p.read_bytes()
if data.startswith(b"\xef\xbb\xbf"):
    p.write_bytes(data[3:])
    print("✅ BOM removed from mangadex_adapter.py")
else:
    print("No BOM found")

import ast
ast.parse(p.read_text(encoding="utf-8"))
print("✅ Syntax OK")