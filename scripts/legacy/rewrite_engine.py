import pathlib

code = '''from backend.automation.model_router import model_router
import os
import logging
import requests
from typing import Dict, Any, Optional

from .models import ContentBrief, ContentDraft
from .prompt_builder import PromptBuilder
from .output_guard import OutputGuard
from .fact_guard import FactGuard
from .styles.profiles import TELEGRAM_AI_EXPERT


logger = logging.getLogger(__name__)


class WritingEngine:
    """
    Writing Engine v1.5.
    
    Оркестратор генерации текста. Платформонезависимый.
    
    Pipeline:
        ContentBrief
            ↓
        PromptBuilder (SYSTEM + STYLE + PLATFORM + <FACTS> + RULES)
            ↓
        LLM (через model_router)
            ↓
        FactGuard (проверка фактов)
            ↓
        OutputGuard (очистка + min_length)
            ↓
        ContentDraft
    
    Подготовка к WritingEngine v2:
    - Автоматический выбор модели (через model_router уже работает)
    - Платформонезависимость (platform в PromptBuilder)
    - <FACTS> теги (против галлюцинаций)
    - ContentDraft контракт (единый интерфейс для всех Publisher)
    """


    def __init__(self, model: Optional[str] = None, platform: str = "telegram"):

        base_url = os.getenv(
            "OLLAMA_URL",
            "http://localhost:11434"
        )

        self.ollama_url = f"{base_url}/api/generate"
        self.model = model or model_router.get_model("writing")
        self.platform = platform


    def generate(
        self,
        brief: ContentBrief,
        style_profile: dict = None
    ) -> dict:
        """
        Генерирует пост из ContentBrief.
        Возвращает dict (обратно совместимо с WritingJob).
        """

        style_profile = style_profile or TELEGRAM_AI_EXPERT

        # Prompt Builder собирает промпт с <FACTS> тегами
        prompt_builder = PromptBuilder(
            style_profile=style_profile,
            platform=self.platform,
            language="ru"
        )
        user_prompt = prompt_builder.build(brief)

        system_prompt = """Ты профессиональный редактор.
Создай готовый пост строго по <FACTS>.
Не добавляй служебные блоки.
Не выдумывай факты.
Начинай сразу с текста поста."""

        logger.info("WritingEngine started model=%s platform=%s", self.model, self.platform)

        result = self._call_ollama(system_prompt, user_prompt)

        if not result:
            raise Exception("Ollama returned empty result")

        generated_text = result.get("response", "").strip()

        if not generated_text:
            raise Exception("Generated text empty")

        # Fact validation layer
        fact_guard = FactGuard()
        facts = getattr(brief, "key_facts", None)
        if facts:
            generated_text = fact_guard.clean(generated_text, facts)

        # Output formatting layer (с min_length проверкой)
        output_guard = OutputGuard()
        generated_text = output_guard.clean(generated_text, min_length=50)

        logger.info("Generated length=%s", len(generated_text))

        # Формируем ContentDraft (для будущей совместимости с v2)
        draft = ContentDraft(
            brief_id=brief.id,
            title=brief.topic,
            body=generated_text,
            model_used=self.model,
            tokens_input=len(user_prompt.split()),
            tokens_output=len(generated_text.split()) if generated_text else 0,
            platform=self.platform
        )

        # Возвращаем dict для обратной совместимости с WritingJob
        return {
            "generated_text": generated_text,
            "tokens_input": draft.tokens_input,
            "tokens_output": draft.tokens_output,
            "model_used": draft.model_used,
            "draft": draft  # Дополнительное поле для будущего использования
        }



    def _call_ollama(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Dict[str, Any]:

        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.35,
                "top_p": 0.90,
                "repeat_penalty": 1.15,
                "num_predict": 900,
                "stop": [
                    "Источник:",
                    "Факты:",
                    "Тема:",
                    "</FACTS>"
                ]
            }
        }

        logger.info("Sending request to Ollama")

        try:
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=(10, 300)
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            logger.exception("Ollama request failed")
            return None
'''

p = pathlib.Path('./engines/writing/engine.py')
p.write_text(code, encoding='utf-8')
print('OK: engine.py переписан — использует PromptBuilder + ContentDraft + <FACTS>')