import pathlib

p = pathlib.Path("/app/core/health.py")
c = p.read_text(encoding="utf-8")

# Добавляем import text
if "from sqlalchemy import text" not in c:
    c = c.replace(
        "from typing import Dict, Any",
        "from typing import Dict, Any\nfrom sqlalchemy import text",
        1,
    )

# Фиксим SELECT 1
old = 'result = db.execute("SELECT 1").scalar()'
new = 'result = db.execute(text("SELECT 1")).scalar()'

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ health.py fixed: text('SELECT 1')")
else:
    print("ℹ️ Already fixed")