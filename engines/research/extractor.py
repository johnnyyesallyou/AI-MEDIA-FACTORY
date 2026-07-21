from typing import Optional
# from core.llm_client import LLMClient
from .models import StructuredFacts

class FactExtractor:
    """
    Извлекает структурированные факты из сырого текста статьи.
    Использует LLM для парсинга и структурирования.
    """
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.extraction_prompt = \"\"\"
Ты — экспертный аналитик фактов. Твоя задача — извлечь ВСЕ факты из статьи 
и представить их в строго структурированном формате.

ПРАВИЛА:
1. Извлекай ТОЛЬКО явные факты из текста
2. НЕ добавляй информацию из своих знаний
3. Сохраняй точные формулировки чисел и дат
4. Выделяй все сущности: компании, люди, продукты
5. Если чего-то нет в тексте — оставь пустой список

Статья:
{article_text}

Верни JSON в формате StructuredFacts.
\"\"\"

    async def extract(self, article_text: str, source_url: str, headline: str) -> StructuredFacts:
        \"\"\"
        Извлекает факты из статьи.
        \"\"\"
        # Здесь будет вызов LLM с response_model=StructuredFacts
        # structured_facts = await self.llm_client.generate_structured(
        #     system_prompt=self.extraction_prompt,
        #     user_prompt=f"Статья: {article_text}",
        #     response_model=StructuredFacts
        # )
        
        # ЗАГЛУШКА для демонстрации:
        return StructuredFacts(
            facts=[
                "OpenAI unveiled GPT-Red.",
                "GPT-Red is an automated red teaming system.",
                "It uses self-play.",
                "Purpose: improve AI safety.",
                "Announced on 2026-07-16."
            ],
            entities=["GPT-Red", "OpenAI"],
            numbers=["2026-07-16"],
            quotes=[],
            keywords=["AI Safety", "Red Teaming"],
            headline=headline,
            source_url=source_url
        )
    
    async def extract_from_url(self, url: str) -> StructuredFacts:
        \"\"\"
        Загружает статью по URL и извлекает факты.
        \"\"\"
        # Здесь будет интеграция с Research Engine
        # article = await self.research_engine.fetch(url)
        # return await self.extract(article.text, url, article.headline)
        pass
