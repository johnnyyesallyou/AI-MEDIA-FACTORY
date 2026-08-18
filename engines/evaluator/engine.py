from backend.automation.model_router import model_router
import os
import json
import asyncio
import re
import logging
import requests
from typing import Optional

from .models import EvaluationResult


logger = logging.getLogger(__name__)


class LLMEvaluatorEngine:
    """
    LLM-as-a-Judge движок оценки качества контента v2.
    
    Архитектура (по видению WritingEngine v2):
        <SOURCE_FACTS> + <POST> + <STYLE> → LLM Judge → EvaluationResult
    
    Отличия от v1 (заглушки):
    - Реальная оценка через LLM (mistral-nemo:12b по умолчанию)
    - Дифференцированные scores (70-95 вместо константных 88)
    - Взвешенная формула overall
    - Детальный feedback от LLM для RevisionJob
    - Fallback на эвристику если LLM упал
    """

    def __init__(self, llm_client=None, model: Optional[str] = None):
        base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_url = f"{base_url}/api/generate"
        
        # Используем лучшую из доступных моделей для оценки — mistral-nemo:12b
        # Можно переопределить через ENV: EVALUATOR_MODEL=llama3.1:8b
        default_eval_model = os.getenv("EVALUATOR_MODEL", "mistral-nemo:12b")
        self.model = model or model_router.get_model("evaluator") or default_eval_model

        self.system_prompt = """Ты — строгий и опытный главный редактор Telegram-канала про технологии и AI.
Твоя задача — объективно оценить сгенерированный пост по 5 критериям.

## КРИТЕРИИ (каждый от 0 до 100):

1. **accuracy** — точность фактов. Сравнивай с <SOURCE_FACTS>. Любое выдуманное число, имя или факт = максимум 40.
2. **clarity** — ясность и структура. Короткие абзацы, логичная последовательность, легко читать.
3. **clickability** — цепляет ли начало? Есть ли hook-вопрос или яркая фраза в первой строке?
4. **telegram_style** — соответствует Telegram-канону: 1-2 эмодзи, 2-4 коротких абзаца, вопрос аудитории в конце, 700-1200 символов.
5. **engagement_prediction** — насколько вероятно, что читатель отреагирует (лайк, коммент, репост)?

## ПРАВИЛА ОЦЕНКИ:

- БУДЬ СТРОГИМ. Отличные посты редки.
- ДИФФЕРЕНЦИРУЙ оценки — не ставь всем одинаковые.
- Шаблонный/сухой текст → clickability и engagement 40-60.
- Живой пост с фактами и hook → 80-95.
- Плохой (пустой, с выдумками, без структуры) → 30-50.

## OVERALL (взвешенная сумма):
overall = accuracy*0.30 + clarity*0.20 + clickability*0.15 + telegram_style*0.20 + engagement_prediction*0.15

## ОТВЕТ:
Строго JSON без markdown, без комментариев. Схема:
{
  "accuracy": <0-100>,
  "clarity": <0-100>,
  "clickability": <0-100>,
  "telegram_style": <0-100>,
  "engagement_prediction": <0-100>,
  "overall": <0-100>,
  "is_approved": <true|false>,
  "feedback_for_regeneration": "<1-3 конкретных предложения на русском если is_approved=false, иначе пустая строка>"
}

is_approved = true ТОЛЬКО если overall >= 80."""

    def evaluate_sync(
        self,
        source_facts: str,
        generated_post: str,
        target_style: str
    ) -> EvaluationResult:
        """Синхронная оценка поста через реальный LLM с fallback на эвристику."""
        
        # Пытаемся получить оценку от LLM
        llm_result = self._call_llm(source_facts, generated_post, target_style)
        
        if llm_result is not None:
            logger.info(
                "LLM Judge model=%s | acc=%s clar=%s click=%s tg=%s eng=%s overall=%s approved=%s",
                self.model,
                llm_result.accuracy, llm_result.clarity, llm_result.clickability,
                llm_result.telegram_style, llm_result.engagement_prediction,
                llm_result.overall, llm_result.is_approved
            )
            return llm_result
        
        # Fallback на эвристику (защита от сбоев LLM)
        logger.warning("LLM Judge failed, using heuristic fallback")
        return self._heuristic_evaluate(source_facts, generated_post, target_style)


    async def evaluate(
        self,
        source_facts: str,
        generated_post: str,
        target_style: str
    ) -> EvaluationResult:
        """
        Async-обёртка: выполняет синхронную оценку в thread pool.
        КРИТИЧНО: не блокирует event loop uvicorn, пока LLM отвечает 5-10 сек.
        """
        return await asyncio.to_thread(
            self.evaluate_sync,
            source_facts,
            generated_post,
            target_style
        )

    def _call_llm(self, source_facts: str, generated_post: str, target_style: str) -> Optional[EvaluationResult]:
        """Вызывает LLM и парсит JSON-ответ."""
        
        user_prompt = f"""## <SOURCE_FACTS>
{source_facts or "(исходные факты отсутствуют)"}
</SOURCE_FACTS>

## <POST>
{generated_post}
</POST>

## <STYLE>
{target_style}
</STYLE>

Оцени пост строго по критериям. Верни ТОЛЬКО JSON без markdown и комментариев."""

        payload = {
            "model": self.model,
            "system": self.system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
                "top_p": 0.85,
                "repeat_penalty": 1.1,
                "num_predict": 600,
            }
        }

        try:
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=(10, 180)
            )
            response.raise_for_status()
            data = response.json()
            
            raw_text = data.get("response", "").strip()
            logger.debug("LLM Judge raw: %s", raw_text[:500])
            
            # Извлекаем JSON (может быть обёрнут в ```json ... ```)
            json_match = re.search(r'\{[\s\S]*\}', raw_text)
            if not json_match:
                logger.error("LLM Judge: no JSON found")
                return None
            
            parsed = json.loads(json_match.group(0))
            
            # Клипим значения в 0-100
            for key in ['accuracy', 'clarity', 'clickability', 'telegram_style', 'engagement_prediction', 'overall']:
                if key in parsed:
                    parsed[key] = max(0, min(100, int(parsed[key])))
            
            # Пересчитываем overall по взвешенной формуле (на случай если LLM его не вычислил)
            if 'overall' not in parsed:
                parsed['overall'] = int(
                    parsed.get('accuracy', 50) * 0.30 +
                    parsed.get('clarity', 50) * 0.20 +
                    parsed.get('clickability', 50) * 0.15 +
                    parsed.get('telegram_style', 50) * 0.20 +
                    parsed.get('engagement_prediction', 50) * 0.15
                )
            
            # is_approved
            if 'is_approved' not in parsed:
                parsed['is_approved'] = parsed['overall'] >= 80
            
            # Feedback
            feedback = parsed.get('feedback_for_regeneration', '')
            if not feedback:
                feedback = (
                    "Пост соответствует требованиям."
                    if parsed['is_approved']
                    else f"Overall {parsed['overall']} < 80. Улучши слабые критерии."
                )
            
            return EvaluationResult(
                accuracy=int(parsed.get('accuracy', 50)),
                clarity=int(parsed.get('clarity', 50)),
                clickability=int(parsed.get('clickability', 50)),
                telegram_style=int(parsed.get('telegram_style', 50)),
                engagement_prediction=int(parsed.get('engagement_prediction', 50)),
                overall=int(parsed['overall']),
                is_approved=bool(parsed['is_approved']),
                feedback_for_regeneration=str(feedback)
            )
            
        except Exception as e:
            logger.exception("LLM Judge failed: %s", e)
            return None

    def _heuristic_evaluate(self, source_facts: str, generated_post: str, target_style: str) -> EvaluationResult:
        """Fallback: эвристическая оценка по длине и структуре."""
        
        post_length = len(generated_post.strip())
        paragraphs = len([p for p in generated_post.split('\n\n') if p.strip()])
        
        if post_length < 100:
            accuracy, clarity, clickability, telegram_style, engagement = 40, 45, 40, 50, 35
        elif post_length < 300:
            accuracy, clarity, clickability, telegram_style, engagement = 60, 65, 55, 60, 50
        elif post_length < 700:
            accuracy, clarity, clickability, telegram_style, engagement = 75, 78, 70, 75, 70
        elif post_length <= 1200:
            accuracy, clarity, clickability, telegram_style, engagement = 85, 87, 80, 88, 82
        else:
            accuracy, clarity, clickability, telegram_style, engagement = 70, 72, 65, 70, 68
        
        # Бонус за параграфы
        if paragraphs >= 2:
            clarity = min(100, clarity + 5)
            telegram_style = min(100, telegram_style + 3)
        
        overall = int(
            accuracy * 0.30 + clarity * 0.20 + clickability * 0.15 + 
            telegram_style * 0.20 + engagement * 0.15
        )
        
        return EvaluationResult(
            accuracy=accuracy,
            clarity=clarity,
            clickability=clickability,
            telegram_style=telegram_style,
            engagement_prediction=engagement,
            overall=overall,
            is_approved=overall >= 80,
            feedback_for_regeneration=(
                "Пост соответствует требованиям."
                if overall >= 80
                else f"Overall={overall}. Улучши структуру, hook-вопрос в начале и конкретику."
            )
        )
