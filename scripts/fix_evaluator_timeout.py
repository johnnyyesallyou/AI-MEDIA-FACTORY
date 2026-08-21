import pathlib

# Ищем evaluator engine
p = pathlib.Path("/app/engines/evaluation/engine.py")
c = p.read_text(encoding="utf-8")

# Увеличиваем timeout с 180 до 300
c = c.replace('timeout=180', 'timeout=300')

p.write_text(c, encoding="utf-8")
print("[OK] Evaluator LLM timeout: 180 -> 300 seconds")