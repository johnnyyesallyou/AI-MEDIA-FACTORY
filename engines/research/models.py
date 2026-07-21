from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StructuredFacts(BaseModel):
    """
    Структурированные факты из статьи.
    Writing Engine получает ТОЛЬКО этот объект, не сырой текст.
    """
    
    # Основные факты (обязательно)
    facts: List[str] = Field(
        description="Список ключевых фактов из статьи. Каждый факт — полное предложение."
    )
    
    # Сущности
    entities: List[str] = Field(
        description="Все упомянутые сущности: компании, люди, продукты, технологии"
    )
    
    # Числа и даты
    numbers: List[str] = Field(
        description="Все цифры, проценты, даты, суммы из статьи"
    )
    
    # Цитаты (если есть)
    quotes: List[str] = Field(
        default_factory=list,
        description="Прямые цитаты из статьи"
    )
    
    # Ключевые слова
    keywords: List[str] = Field(
        default_factory=list,
        description="Основные темы и ключевые слова"
    )
    
    # Заголовок статьи
    headline: str = Field(
        description="Оригинальный заголовок статьи"
    )
    
    # Источник
    source_url: str = Field(
        description="URL исходной статьи"
    )
    
    # Метаданные
    extracted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Время извлечения фактов"
    )
    
    def to_prompt_context(self) -> str:
        """
        Формирует строгий контекст для Writing Engine.
        """
        context = "FACTS:\n"
        for i, fact in enumerate(self.facts, 1):
            context += f"  {i}. {fact}\n"
        
        context += "\nENTITIES:\n"
        for entity in self.entities:
            context += f"  - {entity}\n"
        
        context += "\nNUMBERS:\n"
        for num in self.numbers:
            context += f"  - {num}\n"
        
        if self.quotes:
            context += "\nQUOTES:\n"
            for quote in self.quotes:
                context += f"  - \"{quote}\"\n"
        
        context += "\nKEYWORDS:\n"
        for kw in self.keywords:
            context += f"  - {kw}\n"
        
        context += "\nSTRICT_RULES:\n"
        context += "  - ЗАПРЕЩЕНО использовать информацию, которой нет в FACTS\n"
        context += "  - ЗАПРЕЩЕНО выдумывать сущности, цифры или события\n"
        context += "  - ЗАПРЕЩЕНО изменять контекст или значения\n"
        
        return context
    
    def get_validation_signature(self) -> dict:
        """
        Возвращает сигнатуру для Fact Checker.
        """
        return {
            "entities": sorted(self.entities),
            "numbers": sorted(self.numbers),
            "facts_count": len(self.facts),
            "headline": self.headline
        }
