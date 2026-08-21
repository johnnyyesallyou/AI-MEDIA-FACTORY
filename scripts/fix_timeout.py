import pathlib

p = pathlib.Path("/app/engines/writing/engine.py")
c = p.read_text(encoding="utf-8")

# Увеличиваем timeout с 120 до 300 секунд
c = c.replace('timeout=120', 'timeout=300')

p.write_text(c, encoding="utf-8")
print("[OK] LLM timeout: 120 -> 300 seconds")