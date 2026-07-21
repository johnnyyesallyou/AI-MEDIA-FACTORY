from pydantic import BaseModel, Field
from typing import Dict, Optional
from enum import Enum

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    GEMMA = "gemma"

class ModelConfig(BaseModel):
    """
    Конфигурация конкретной LLM.
    Позволяет добавлять новые модели без изменения кода движков.
    """
    id: str = Field(description="Уникальный идентификатор модели, например 'qwen3-32b'")
    provider: LLMProvider
    model_name: str = Field(description="Точное название модели в API провайдера")
    context_window: int = Field(default=8192, description="Максимальное количество токенов контекста")
    max_output_tokens: int = Field(default=2048, description="Максимальное количество токенов в ответе")
    api_key_env_var: Optional[str] = Field(default=None, description="Имя переменной окружения для API ключа")
    base_url: Optional[str] = Field(default=None, description="Кастомный URL (например, для локального Ollama)")

class TaskRoutingRule(BaseModel):
    """
    Правило маршрутизации для конкретной задачи.
    """
    task_name: str = Field(description="Название задачи: 'research', 'writing', 'fact_check', 'evaluator'")
    primary_model_id: str = Field(description="ID основной модели для этой задачи")
    fallback_model_id: Optional[str] = Field(default=None, description="ID резервной модели при сбое основной")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Креативность генерации")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Ядерная выборка")

class ModelRoutingConfig(BaseModel):
    """
    Глобальная конфигурация роутинга моделей.
    """
    available_models: Dict[str, ModelConfig]
    task_rules: Dict[str, TaskRoutingRule]

    def get_routing_for_task(self, task_name: str) -> tuple[ModelConfig, TaskRoutingRule]:
        """
        Возвращает конфигурацию модели и правила для заданной задачи.
        """
        if task_name not in self.task_rules:
            raise ValueError(f"Правило роутинга для задачи '{task_name}' не найдено.")
        
        rule = self.task_rules[task_name]
        if rule.primary_model_id not in self.available_models:
            raise ValueError(f"Основная модель '{rule.primary_model_id}' не найдена в доступных моделях.")
        
        return self.available_models[rule.primary_model_id], rule

    def get_fallback_model(self, task_name: str) -> Optional[ModelConfig]:
        """
        Возвращает резервную модель, если она указана для задачи.
        """
        rule = self.task_rules.get(task_name)
        if rule and rule.fallback_model_id and rule.fallback_model_id in self.available_models:
            return self.available_models[rule.fallback_model_id]
        return None
