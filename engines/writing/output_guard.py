import re
import logging


logger = logging.getLogger(__name__)


class OutputGuard:
    """
    Очистка результата LLM перед сохранением в БД.
    Удаляет служебные элементы, которые модель может добавить.
    """

    forbidden_headers = [
        "заголовок:",
        "текст:",
        "источник:",
        "основные факты:",
        "факты:",
        "тема:",
        "абзац 1:",
        "абзац 2:",
        "абзац 3:",
        "важность:",
        "ключевые моменты:",
        "вопрос для аудитории:",
        "вопрос:"
    ]


    def clean(self, text: str, min_length: int = 50) -> str:
        """
        Очищает результат LLM от служебных элементов.
        
        Если после очистки текст короче min_length символов — возвращает пустую строку,
        чтобы WritingJob пометил пост как needs_revision (вместо сохранения пустого драфта).
        """

        if not text:
            return ""


        result = text.strip()
        
        # Ранняя проверка: если исходник слишком короткий — не тратим время
        if len(result) < min_length:
            logger.warning(f"OutputGuard: text too short before cleaning ({len(result)} < {min_length})")
            return ""


        # Убираем markdown-разделители
        result = re.sub(
            r"^---+",
            "",
            result,
            flags=re.MULTILINE
        )


        # Убираем служебные заголовки
        for header in self.forbidden_headers:

            result = re.sub(
                re.escape(header),
                "",
                result,
                flags=re.IGNORECASE
            )


        # Убираем ссылки
        result = re.sub(
            r"https?://\S+",
            "",
            result
        )


        # Убираем жирные markdown заголовки
        result = re.sub(
            r"\*\*(.*?)\*\*",
            r"\1",
            result
        )


        # Чистим пустые строки
        result = re.sub(
            r"\n{3,}",
            "\n\n",
            result
        )

        result = result.strip()
        
        # Финальная проверка: если после очистки слишком короткий — возвращаем пустую строку
        if len(result) < min_length:
            logger.warning(f"OutputGuard: text too short after cleaning ({len(result)} < {min_length})")
            return ""

        return result