import pathlib

# Правильный путь: engines/evaluator/engine.py
p = pathlib.Path("/app/engines/evaluator/engine.py")
c = p.read_text(encoding="utf-8")

# Заменяем mistral-nemo:12b на gemma2:9b
c = c.replace('mistral-nemo:12b', 'gemma2:9b')
c = c.replace('llama3.1:8b', 'gemma2:9b')

p.write_text(c, encoding="utf-8")
print("[OK] Evaluator engine: using gemma2:9b")