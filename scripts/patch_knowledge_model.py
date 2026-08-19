import pathlib

p = pathlib.Path("/app/core/models/manga_knowledge.py")
c = p.read_text(encoding="utf-8")

if "sources_data" not in c:
    marker = "    external_ids = Column(JSONB, default=dict)"
    if marker in c:
        c = c.replace(
            marker,
            marker + "\n    # Сырые данные из каждого источника (Sprint 26)\n    sources_data = Column(JSONB, default=dict)",
            1,
        )
        p.write_text(c, encoding="utf-8")
        import ast; ast.parse(c)
        print("✅ Model patched: sources_data")
    else:
        print("❌ Marker not found")
else:
    print("ℹ️ Already patched")