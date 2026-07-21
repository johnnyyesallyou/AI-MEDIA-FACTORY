from typing import Dict, Any
# from core.llm_client import LLMClient
from .models import EvaluationResult

class LLMEvaluatorEngine:
    """
    Движок оценки качества контента.
    Работает как независимый 'судья' (LLM-as-a-Judge).
    """
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.system_prompt = \"\"\"
Ты — строгий и опытный главный редактор Telegram-канала и эксперт по оценке AI-контента.
Твоя задача — оценить качество сгенерированного поста по 5 критериям (от 0 до 100) и вынести вердикт.

КРИТЕРИИ ОЦЕНКИ:
1. Accuracy (Точность): Насколько точно пост передает смысл исходных фактов без искажений.
2. Clarity (Ясность): Насколько текст легко читается, логичен и хорошо структурирован.
3. Clickability (Кликабельность): Насколько цепляет заголовок и первые строки (hook).
4. Telegram Style: Соблюдение формата Telegram (короткие абзацы, уместные эмодзи, живой язык).
5. Engagement Prediction: Насколько высока вероятность, что пост вызовет реакции, комментарии или репосты.

ПРАВИЛА ВЕРДИКТА:
- Вычисли overall (среднее или взвешенное значение).
- Если overall >= 80: is_approved = True.
- Если overall < 80: is_approved = False, и в feedback_for_regeneration напиши 1-2 конкретных предложения, что именно нужно исправить автору (Writing Engine), чтобы пост стал лучше.

Верни строго JSON в формате EvaluationResult.
\"\"\"

    async def evaluate(self, source_facts: str, generated_post: str, target_style: str) -> EvaluationResult:
        \"\"\"
        Оценивает сгенерированный пост на основе исходных фактов и целевого стиля.
        \"\"\"
        user_prompt = f\"\"\"
<SOURCE_FACTS>
{source_facts}
</SOURCE_FACTS>

<TARGET_STYLE>
{target_style}
</TARGET_STYLE>

<GENERATED_POST_TO_EVALUATE>
{generated_post}
</GENERATED_POST_TO_EVALUATE>

Проведи оценку и верни JSON.
\"\"\"
        
        # В реальной реализации здесь будет вызов LLM:
        # result = await self.llm_client.generate_structured(
        #     system_prompt=self.system_prompt,
        #     user_prompt=user_prompt,
        #     response_model=EvaluationResult
        # )
        # return result
        
        # ЗАГЛУШКА для демонстрации успешной оценки:
        return EvaluationResult(
            accuracy=96,
            clarity=91,
            clickability=88,
            telegram_style=95,
            engagement_prediction=82,
            overall=90,
            is_approved=True,
            feedback_for_regeneration="Пост отличный, можно публиковать."
        )
