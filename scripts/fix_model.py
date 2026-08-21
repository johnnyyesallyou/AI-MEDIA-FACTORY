import pathlib

# Writing engine
p1 = pathlib.Path("/app/engines/writing/engine.py")
c1 = p1.read_text(encoding="utf-8")
c1 = c1.replace('mistral-nemo:12b', 'gemma2:9b')
c1 = c1.replace('llama3.1:8b', 'gemma2:9b')
p1.write_text(c1, encoding="utf-8")
print("[OK] Writing engine: using gemma2:9b")

# Evaluation engine
p2 = pathlib.Path("/app/engines/evaluation/engine.py")
c2 = p2.read_text(encoding="utf-8")
c2 = c2.replace('mistral-nemo:12b', 'gemma2:9b')
c2 = c2.replace('llama3.1:8b', 'gemma2:9b')
p2.write_text(c2, encoding="utf-8")
print("[OK] Evaluation engine: using gemma2:9b")