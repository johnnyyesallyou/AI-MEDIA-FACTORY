import pathlib, re

p = pathlib.Path("/app/core/models/channel_orm.py")
c = p.read_text(encoding="utf-8")

changed = False

# 1. Импорт JSONB
if "content_profile" not in c:
    if "JSONB" not in c:
        c = c.replace(
            "from sqlalchemy import",
            "from sqlalchemy.dialects.postgresql import JSONB\nfrom sqlalchemy import",
            1
        )
        changed = True

    # 2. Колонка перед первым def в классе
    lines = c.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("    def "):
            lines.insert(i, "    content_profile = Column(JSONB, nullable=True)\n")
            changed = True
            break
    c = "".join(lines)

if changed:
    p.write_text(c, encoding="utf-8")
    import ast
    ast.parse(c)
    print("✅ Model patched: content_profile JSONB added")
else:
    print("ℹ️ Model already patched")