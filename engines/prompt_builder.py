"""Prompt Builder - Sprint 60.

Объединяет FACTS + CONTEXT + STYLE + RULES в единый промпт для WritingEngine.

Архитектура:
  Channel Profile
       ↓
  ChannelContext (learnings + history)
       ↓
  PromptBuilder
       ↓
  WritingEngine (LLM)
       ↓
  Content
"""
from typing import Dict, List, Optional
from engines.content_context import ChannelContext


class PromptBuilder:
    """Строит промпт для LLM с учётом контекста канала."""

    def __init__(self, context: ChannelContext):
        self.context = context
        self.ctx = context.to_prompt_context()

    def build_news_prompt(self, article: dict) -> str:
        """Построить промпт для новостного поста."""
        patterns = ", ".join(self.ctx["working_patterns"][:3]) if self.ctx["working_patterns"] else "ещё нет данных"
        
        prompt = f"""Ты — редактор Telegram-канала "{self.ctx['channel_name']}".
Тема канала: {self.ctx['theme']}
Аудитория: {self.ctx['audience']}
Язык: {self.ctx['language']}

Что хорошо работает на этом канале:
{patterns}

Последние публикации (для стиля):
{self.ctx['recent_posts_summary'] or 'пока нет'}

---

НОВОСТЬ:
Заголовок: {article.get('title', '')}
Источник: {article.get('source_name', '')}
Описание: {article.get('summary', article.get('description', ''))[:500]}

---

ЗАДАЧА:
Напиши пост для Telegram на основе этой новости.

ТРЕБОВАНИЯ:
1. Язык: {self.ctx['language']}
2. Длина: 150-300 символов
3. Стиль: {self.ctx['style']}
4. Используй паттерны которые работают (если есть)
5. Добавь эмодзи в начало (📰, 🔥, ⚡)
6. НЕ добавляй хештеги (они добавляются отдельно)
7. НЕ добавляй ссылки (они добавляются отдельно)

ПОСТ:"""
        return prompt

    def build_manga_prompt(self, manga_title: dict, chapter_number: str) -> str:
        """Построить промпт для манга-поста."""
        patterns = ", ".join(self.ctx["working_patterns"][:3]) if self.ctx["working_patterns"] else "ещё нет данных"
        
        prompt = f"""Ты — редактор Telegram-канала "{self.ctx['channel_name']}".
Тема канала: {self.ctx['theme']}
Аудитория: {self.ctx['audience']}
Язык: {self.ctx['language']}

Что хорошо работает на этом канале:
{patterns}

---

МАНГА:
Название: {manga_title.get('title_ru', manga_title.get('title', ''))}
Оригинальное: {manga_title.get('title_en', '')}
Жанры: {', '.join(manga_title.get('genres', []))}
Описание: {manga_title.get('description', '')[:300]}
Новая глава: {chapter_number}

---

ЗАДАЧА:
Напиши короткое описание для анонса новой главы.

ТРЕБОВАНИЯ:
1. Язык: {self.ctx['language']}
2. Длина: 100-200 символов
3. Упомяни жанры
4. Краткое интригующее описание
5. БЕЗ хештегов (они добавляются отдельно)

ОПИСАНИЕ:"""
        return prompt

    def build_generic_prompt(self, facts: dict, content_type: str) -> str:
        """Универсальный промпт для любого типа контента."""
        patterns = ", ".join(self.ctx["working_patterns"][:3]) if self.ctx["working_patterns"] else "ещё нет данных"
        
        prompt = f"""Ты — редактор Telegram-канала "{self.ctx['channel_name']}".
Тема канала: {self.ctx['theme']}
Аудитория: {self.ctx['audience']}
Язык: {self.ctx['language']}
Тип контента: {content_type}

Что хорошо работает на этом канале:
{patterns}

---

ФАКТЫ:
{self._format_facts(facts)}

---

ЗАДАЧА:
Напиши пост для Telegram на основе этих фактов.

ТРЕБОВАНИЯ:
1. Язык: {self.ctx['language']}
2. Длина: 150-300 символов
3. Стиль: {self.ctx['style']}
4. Используй паттерны которые работают (если есть)
5. БЕЗ хештегов и ссылок (они добавляются отдельно)

ПОСТ:"""
        return prompt

    def _format_facts(self, facts: dict) -> str:
        """Форматировать факты для промпта."""
        lines = []
        for key, value in facts.items():
            if isinstance(value, list):
                lines.append(f"{key}: {', '.join(str(v) for v in value[:5])}")
            elif isinstance(value, str) and len(value) > 200:
                lines.append(f"{key}: {value[:200]}...")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)