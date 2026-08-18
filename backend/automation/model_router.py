import os

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
