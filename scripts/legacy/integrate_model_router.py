import pathlib

# 1. Создаём backend/automation/model_router.py
router_code = '''"""
Централизованный роутер моделей.
Движки читают отсюда, а не из env напрямую.
"""
import os
from typing import Optional

class ModelRouter:
    def __init__(self):
        # In-memory хранилище (можно заменить на БД)
        self._routing = {
            "writing": os.getenv("WRITING_MODEL", "llama3.2:3b"),
            "evaluator": os.getenv("EVALUATOR_MODEL", "llama3.2:3b"),
            "research": os.getenv("RESEARCH_MODEL", "llama3.2:3b"),
            "fact_check": os.getenv("FACT_CHECK_MODEL", "llama3.2:3b"),
        }
    
    def get_model(self, task: str) -> str:
        """Получить модель для задачи."""
        return self._routing.get(task, self._routing.get("writing", "llama3.2:3b"))
    
    def set_model(self, task: str, model: str):
        """Установить модель для задачи."""
        self._routing[task] = model
    
    def get_all(self) -> dict:
        """Получить все роутинги."""
        return self._routing.copy()

# Глобальный экземпляр
model_router = ModelRouter()
'''

p = pathlib.Path('./backend/automation/model_router.py')
p.write_text(router_code, encoding='utf-8')
print('OK: model_router.py created')

# 2. Патчим WritingEngine
we = pathlib.Path('./engines/writing/engine.py')
s = we.read_text(encoding='utf-8')

if 'model_router' not in s:
    # Добавляем импорт в начало
    s = 'from backend.automation.model_router import model_router\n' + s
    
    # Заменяем чтение модели из env на model_router
    old_init = '''        self.model = (
            model
            or os.getenv(
                "WRITING_MODEL",
                "llama3.2:3b",
            )
        )'''
    new_init = '''        self.model = model or model_router.get_model("writing")'''
    
    if old_init in s:
        s = s.replace(old_init, new_init)
        print('OK: WritingEngine patched to use model_router')
    
    we.write_text(s, encoding='utf-8')

# 3. Патчим ai.py (чтобы PUT /ai/routing обновлял model_router)
ai = pathlib.Path('./backend/app/api/v1/ai.py')
s = ai.read_text(encoding='utf-8')

if 'model_router' not in s:
    # Добавляем импорт
    s = 'from backend.automation.model_router import model_router\n' + s
    
    # Патчим update_task_routing
    old_update = '''    _current_routing[update.task_name] = {
        "model": update.model_id,
        "fallback": _current_routing[update.task_name]["fallback"],
        "temperature": update.temperature,
    }'''
    new_update = '''    _current_routing[update.task_name] = {
        "model": update.model_id,
        "fallback": _current_routing[update.task_name]["fallback"],
        "temperature": update.temperature,
    }
    # Обновляем model_router, чтобы движки подхватили
    model_router.set_model(update.task_name, update.model_id)'''
    
    if old_update in s:
        s = s.replace(old_update, new_update)
        print('OK: ai.py patched to update model_router')
    
    ai.write_text(s, encoding='utf-8')

print('DONE: ModelRouter integrated')