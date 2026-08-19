import pathlib

p = pathlib.Path("/app/engines/source_adapters/mangadex_adapter.py")
c = p.read_text(encoding="utf-8")

changed = False

# 1. Signature
old_sig = "def fetch_latest_chapters(self, limit: int = 20) -> List[SourceItem]:"
new_sig = "def fetch_latest_chapters(self, limit: int = 20, offset: int = 0) -> List[SourceItem]:"
if old_sig in c:
    c = c.replace(old_sig, new_sig)
    changed = True
    print("Signature patched")

# 2. Params: cap limit at 100 (MangaDex max) + offset
old_limit = '("limit", limit * 2),'
new_limit = '("limit", min(limit * 2, 100)),\n                ("offset", offset),'
if old_limit in c and '("offset", offset),' not in c:
    c = c.replace(old_limit, new_limit)
    changed = True
    print("Params patched (limit cap 100 + offset)")

if changed:
    p.write_text(c, encoding="utf-8")
    import ast
    ast.parse(c)
    print("Syntax OK")
else:
    print("No changes needed")
