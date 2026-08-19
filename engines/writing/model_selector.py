"""
Model Selector для WritingEngine v2.

Автоматически выбирает модель в зависимости от типа контента:
- Новости → быстрая модель (llama3.1:8b)
- Аналитика → качественная модель (mistral-nemo:12b)
- Маркетинг → креативная модель (llama3.1:8b)
- Научная статья → точная модель (mistral-nemo:12b)
"""
import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


class ModelSelector:
    """Выбирает оптимальную модель для генерации контента."""
    
    # Маппинг типов контента на модели
    MODEL_MAPPING = {
        "news": "llama3.1:8b",           # Быстрая для новостей
        "analytics": "mistral-nemo:12b", # Качественная для аналитики
        "marketing": "llama3.1:8b",      # Креативная для маркетинга
        "scientific": "mistral-nemo:12b", # Точная для научных статей
        "tutorial": "llama3.1:8b",       # Для обучающих материалов
        "opinion": "llama3.1:8b",        # Для мнений и комментариев
        "review": "mistral-nemo:12b",    # Для обзоров (нужна точность)
    }
    
    # Ключевые слова для определения типа контента
    CONTENT_TYPE_KEYWORDS = {
        "news": ["новость", "сообщает", "представила", "анонсировала", "запустила", "news", "announced", "launched"],
        "analytics": ["анализ", "исследование", "статистика", "данные", "показывает", "analysis", "research", "data"],
        "marketing": ["продукт", "решение", "помогает", "улучшает", "выгода", "product", "solution", "benefit"],
        "scientific": ["исследование", "ученые", "эксперимент", "теория", "гипотеза", "research", "study", "experiment"],
        "tutorial": ["как", "руководство", "инструкция", "шаг", "обучение", "how to", "guide", "tutorial"],
        "opinion": ["мнение", "считает", "полагает", "думает", "мнение эксперта", "opinion", "believes", "thinks"],
        "review": ["обзор", "тест", "проверка", "сравнение", "плюсы", "минусы", "review", "test", "comparison"],
    }
    
    def __init__(self, default_model: str = "llama3.1:8b"):
        self.default_model = default_model
    
    def detect_content_type(self, brief: Any) -> str:
        """Определяет тип контента по brief."""
        # Собираем весь текст для анализа
        text_to_analyze = ""
        if hasattr(brief, 'topic'):
            text_to_analyze += brief.topic + " "
        if hasattr(brief, 'goal'):
            text_to_analyze += brief.goal + " "
        if hasattr(brief, 'key_facts') and brief.key_facts:
            text_to_analyze += " ".join(brief.key_facts)
        
        text_lower = text_to_analyze.lower()
        
        # Подсчитываем совпадения для каждого типа
        scores = {}
        for content_type, keywords in self.CONTENT_TYPE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[content_type] = score
        
        # Возвращаем тип с наибольшим количеством совпадений
        if scores:
            detected_type = max(scores, key=scores.get)
            logger.info(f"ModelSelector: detected content type '{detected_type}' (score: {scores[detected_type]})")
            return detected_type
        
        logger.info(f"ModelSelector: no content type detected, using default")
        return "news"  # По умолчанию новости
    
    def select_model(self, brief: Any, override_model: str = None) -> str:
        """Выбирает модель для генерации."""
        if override_model:
            logger.info(f"ModelSelector: using override model '{override_model}'")
            return override_model
        
        content_type = self.detect_content_type(brief)
        selected_model = self.MODEL_MAPPING.get(content_type, self.default_model)
        
        logger.info(f"ModelSelector: content_type='{content_type}' -> model='{selected_model}'")
        return selected_model