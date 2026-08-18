"""
Prompt Builder v1.5 — платформонезависимый сборщик промптов.

Архитектура (по видению WritingEngine v2):
    SYSTEM + STYLE + PLATFORM + <FACTS> + RULES

Это вынесенная логика сборки промпта из engine.py.
Engine остаётся оркестратором, не зная деталей промпта.
"""

import logging
from typing import Dict, Any, List

from .models import ContentBrief


logger = logging.getLogger(__name__)


class PromptBuilder:
    """Собирает промпт из частей: system, style, platform, facts, rules."""

    def __init__(
        self,
        style_profile: Dict[str, Any],
        platform: str = "telegram",
        language: str = "ru"
    ):
        self.profile = style_profile
        self.platform = platform
        self.language = language

    def build(self, brief: ContentBrief) -> str:
        """Собирает финальный промпт для LLM."""
        parts = [
            self._build_system(),
            self._build_style(),
            self._build_platform_rules(),
            self._build_topic(brief),
            self._build_facts(brief),
            self._build_goal(brief),
            self._build_format_rules(brief),
            self._build_final_instruction()
        ]
        return "\n\n".join(parts)

    def _build_system(self) -> str:
        return """## SYSTEM

Ты — профессиональный редактор технологического медиа.
Твоя задача — написать качественный пост для публикации.

СТРОГИЕ ПРИНЦИПЫ:
- Используй ТОЛЬКО информацию из блока <FACTS>.
- Никогда не додумывай, не придумывай, не добавляй от себя.
- Не упоминай людей, компании, цифры без подтверждения в <FACTS>.
- Если информации мало — сделай короткий, но точный пост.
- Пиши живо, но без кликбейта и преувеличений."""

    def _build_style(self) -> str:
        tone = self.profile.get("tone", "экспертный")
        audience = self.profile.get("audience", "IT специалисты")
        return f"""## STYLE

Тон: {tone}
Аудитория: {audience}
Язык: {self.language}"""

    def _build_platform_rules(self) -> str:
        """Правила специфичные для платформы."""
        if self.platform == "telegram":
            return """## PLATFORM (Telegram)

- Начни с цепляющего заголовка (одна строка, без ###).
- Используй 1-2 релевантных эмодзи в заголовке или первом абзаце.
- 2-4 коротких абзаца (каждый по 1-3 предложения).
- В конце — короткий вопрос аудитории для вовлечения.
- Общая длина: 700-1200 символов.
- Без markdown-разметки (**жирный**, ### заголовки)."""
        elif self.platform == "vk":
            return """## PLATFORM (VK)

- Более развёрнутый текст (1500-2500 символов).
- Можно использовать списки.
- Хэштеги в конце."""
        else:
            return f"""## PLATFORM ({self.platform})

- Стандартный формат поста."""

    def _build_topic(self, brief: ContentBrief) -> str:
        return f"""## TOPIC

{brief.topic}"""

    def _build_facts(self, brief: ContentBrief) -> str:
        """КЛЮЧЕВОЕ ИЗ АРХИТЕКТУРЫ: <FACTS> теги против галлюцинаций."""
        if not brief.key_facts:
            facts_text = "(факты отсутствуют — напиши короткий пост-вопрос)"
        else:
            facts_text = "\n".join(f"- {fact}" for fact in brief.key_facts)

        return f"""## <FACTS>

Используй ТОЛЬКО эти факты. Ничего больше.

{facts_text}

</FACTS>"""

    def _build_goal(self, brief: ContentBrief) -> str:
        return f"""## GOAL

{brief.goal}"""

    def _build_format_rules(self, brief: ContentBrief) -> str:
        """Запреты и ограничения."""
        forbidden = getattr(brief, 'forbidden_words', []) or []
        forbidden_str = ", ".join(forbidden) if forbidden else "спам, кликбейт, шок"
        
        return f"""## RULES

НЕ ИСПОЛЬЗУЙ:
- Слова: {forbidden_str}
- Служебные блоки: "Источник:", "Факты:", "Тема:", "Анализ:"
- Заголовки вроде "Важная информация", "Обзор", "Основные моменты"
- Markdown-разметку (###, **, __)
- URL и ссылки
- Объяснения своих действий
- Списки (если платформа не VK)

ФОРМАТ ОТВЕТА:
- Только готовый текст поста.
- Без преамбулы и заключения.
- Начни сразу с заголовка."""

    def _build_final_instruction(self) -> str:
        return """Напиши пост на основе <FACTS>. Верни ТОЛЬКО готовый текст."""
