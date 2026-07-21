from typing import Dict, Any
# from core.llm_client import LLMClient
# from engines.research.models import StructuredFacts
from .models import FactCheckResult

class FactCheckerEngine:
    """
    Движок проверки фактов.
    Сравнивает сгенерированный пост с исходными структурированными фактами.
    """
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.system_prompt = \"\"\"
Ты — строгий фактчекер системы AI-MEDIA-FACTORY. 
Твоя задача — проверить сгенерированный пост на соответствие исходным фактам.

Проведи 5 обязательных проверок:
1. ENTITIES: Все ли сущности из источника упомянуты корректно и НЕТ ли новых выдуманных сущностей?
2. NUMBERS: Все ли цифры, даты и числа точно совпадают с источником?
3. FACTS: Нет ли выдуманных фактов, событий или причинно-следственных связей, которых не было в источнике?
4. HEADLINE: Соответствует ли тема и заголовок поста исходной статье?
5. STYLE: Соблюден ли запрошенный стиль?

ПРАВИЛА ОЦЕНКИ:
- Если найдена хотя бы одна критическая галлюцинация (выдуманная сущность, цифра или факт) — статус ДОЛЖЕН быть "Rejected", а оценка ниже 50.
- Если все проверки пройдены успешно — статус "Approved", оценка 90-100.

Верни строго JSON в формате FactCheckResult.
\"\"\"

    async def check(self, source_facts: Dict[str, Any], generated_post: str) -> FactCheckResult:
        \"\"\"
        Проверяет пост на основе сигнатуры исходных фактов.
        
        :param source_facts: Словарь с ключами 'entities', 'numbers', 'headline', 'facts'
        :param generated_post: Текст сгенерированного поста
        :return: FactCheckResult
        \"\"\"
        user_prompt = f\"\"\"
<SOURCE_DATA>
Headline: {source_facts.get('headline', 'N/A')}
Entities: {source_facts.get('entities', [])}
Numbers: {source_facts.get('numbers', [])}
Facts: {source_facts.get('facts', [])}
</SOURCE_DATA>

<GENERATED_POST>
{generated_post}
</GENERATED_POST>

Проведи 5 проверок и верни оценку в формате JSON.
\"\"\"
        
        # В реальной реализации здесь будет вызов LLM:
        # result = await self.llm_client.generate_structured(
        #     system_prompt=self.system_prompt,
        #     user_prompt=user_prompt,
        #     response_model=FactCheckResult
        # )
        # return result
        
        # ЗАГЛУШКА для демонстрации успешного прохождения:
        return FactCheckResult(
            status="Approved",
            score=93,
            entities_valid=True,
            numbers_valid=True,
            facts_valid=True,
            headline_valid=True,
            style_valid=True,
            missing_entities=[],
            hallucinated_entities=[],
            hallucinated_facts=[],
            reasoning="Пост точно отражает предоставленные факты. Все сущности (OpenAI, GPT-Red) и цифры (2026-07-16) на месте. Галлюцинаций не обнаружено."
        )
