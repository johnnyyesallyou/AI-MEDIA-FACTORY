import pathlib

p = pathlib.Path("/app/engines/telegram/engine.py")
c = p.read_text(encoding="utf-8")

# Фиксим два места где text_length=result["text_length"]
c = c.replace(
    'text_length=result["text_length"]',
    'text_length=result.get("text_length", len(text))',
)

p.write_text(c, encoding="utf-8")
print("[OK] telegram engine: text_length safe fallback")