import pathlib

# 0. Переписываем model_router с правильным дефолтом (llama3.1:8b есть в Ollama)
mr = '''import os

class ModelRouter:
    def __init__(self):
        self._routing = {
            "writing": os.getenv("WRITING_MODEL", "llama3.1:8b"),
            "evaluator": os.getenv("EVALUATOR_MODEL", "llama3.1:8b"),
            "research": os.getenv("RESEARCH_MODEL", "llama3.1:8b"),
            "fact_check": os.getenv("FACT_CHECK_MODEL", "llama3.1:8b"),
        }

    def get_model(self, task):
        return self._routing.get(task, "llama3.1:8b")

    def set_model(self, task, model):
        self._routing[task] = model

    def get_all(self):
        return self._routing.copy()

model_router = ModelRouter()
'''
pathlib.Path('./backend/automation/model_router.py').write_text(mr, encoding='utf-8')
print('OK: model_router.py rewritten (default llama3.1:8b)')

# 1. WritingEngine: убираем BOM (utf-8-sig), чистый импорт, точный патч init
we = pathlib.Path('./engines/writing/engine.py')
s = we.read_text(encoding='utf-8-sig')
lines = [l for l in s.split('\n') if 'from backend.automation.model_router' not in l]
s = 'from backend.automation.model_router import model_router\n' + '\n'.join(lines)
old_init = '''        self.model = (
            model
            or os.getenv(
                "WRITING_MODEL",
                "llama3.1:8b"
            )
        )'''
if old_init in s:
    s = s.replace(old_init, '        self.model = model or model_router.get_model("writing")')
    print('OK: WritingEngine init -> model_router')
else:
    print('WARN: init pattern not found')
we.write_text(s, encoding='utf-8')

# 2. ai.py: убираем BOM, чистый импорт, set_model + live-валидация по Ollama
ai = pathlib.Path('./backend/app/api/v1/ai.py')
s = ai.read_text(encoding='utf-8-sig')
lines = [l for l in s.split('\n') if 'from backend.automation.model_router' not in l]
s = 'import os\nfrom backend.automation.model_router import model_router\n' + '\n'.join(lines)

old_update = '''    _current_routing[update.task_name] = {
        "model_id": update.model_id,
        "fallback": _current_routing[update.task_name]["fallback"],
        "temperature": update.temperature
    }'''
if old_update in s and 'model_router.set_model' not in s:
    s = s.replace(old_update, old_update + '\n    model_router.set_model(update.task_name, update.model_id)')
    print('OK: ai.py -> model_router.set_model added')

old_val = '''    if update.model_id not in _available_models:
        raise HTTPException(status_code=400, detail="Model not available")'''
new_val = '''    try:
        import requests as _rq
        _live = [m.get("name", "") for m in _rq.get(os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/tags", timeout=3).json().get("models", [])]
    except Exception:
        _live = []
    if update.model_id not in _available_models and update.model_id not in _live:
        raise HTTPException(status_code=400, detail="Model not available")'''
if old_val in s:
    s = s.replace(old_val, new_val)
    print('OK: live Ollama validation added')
ai.write_text(s, encoding='utf-8')

print('DONE')