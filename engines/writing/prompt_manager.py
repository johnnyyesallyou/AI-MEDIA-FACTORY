import logging
from typing import Dict, Any

from .models import ContentBrief


logger = logging.getLogger(__name__)


class PromptManager:

    def __init__(
        self,
        style_profile: Dict[str, Any]
    ):
        self.profile = style_profile


    def build_prompt(
        self,
        brief: ContentBrief
    ) -> str:

        facts = "\n".join(
            f"- {fact}"
            for fact in brief.key_facts
        )


        return f"""
Ты редактор профессионального Telegram-канала про технологии и AI.

Напиши один готовый пост для публикации.

КРИТИЧЕСКИ ВАЖНО:

- Используй ТОЛЬКО информацию из блока ФАКТЫ.
- Не добавляй знания из своей памяти.
- Не придумывай интервью, цитаты, мнения и цифры.
- Не расширяй тему.
- Не объясняй то, чего нет в фактах.
- Не упоминай источник.
- Не показывай URL.
- Не используй слова:
  "Источник"
  "Факты"
  "Тема"
  "Анализ"
- Не пиши заголовки вроде:
  "Важная информация"
  "Обзор"
  "Основные моменты"


ЯЗЫК:

Только русский.


СТИЛЬ:

Тон:
{self.profile.get("tone","экспертный")}

Аудитория:
{self.profile.get("audience","IT специалисты")}


ТЕМА:

{brief.topic}


ФАКТЫ:

{facts}


ЦЕЛЬ:

{brief.goal}


ТРЕБУЕМЫЙ ФОРМАТ:

Начни сразу с короткого заголовка.

После заголовка:
2-4 коротких абзаца.

В конце:
один вопрос аудитории.


НЕ ПИШИ:

- Markdown-разметку уровня ###
- списки
- служебные комментарии
- объяснение своих действий


Верни только готовый Telegram-пост.
"""
