import re
import logging
from typing import List, Union


logger = logging.getLogger(__name__)


class FactGuard:
    """
    FactGuard v2.

    Проверяет сгенерированный текст относительно
    исходных фактов и удаляет неподтвержденные утверждения.
    """


    def clean(
        self,
        text: str,
        facts: Union[str, List[str]]
    ) -> str:


        if not text:
            return text


        if isinstance(facts, list):

            source = " ".join(
                facts
            )

        else:

            source = facts


        source_lower = source.lower()


        lines = []

        removed = 0


        sentences = re.split(
            r'(?<=[.!?])\s+',
            text
        )


        for sentence in sentences:

            sentence_lower = sentence.lower()


            if not sentence.strip():
                continue


            # удаляем ссылки

            if "http://" in sentence_lower or "https://" in sentence_lower:
                removed += 1
                continue



            # удаляем неподтвержденные числа

            numbers = re.findall(
                r'\d+',
                sentence
            )


            for number in numbers:

                if number not in source:

                    logger.warning(
                        "Removed unsupported number: %s",
                        number
                    )

                    sentence = ""

                    removed += 1
                    break


            if not sentence:
                continue



            forbidden = [

                "революцион",
                "изменит рынок",
                "лидер рынка",
                "крупнейшая компания",
                "миллионы пользователей",
                "эксперты считают",
                "значительно улучшит",
                "гарантирует",
                "навсегда изменит",
                "лучшее решение",
                "уникальная технология",
                "прорывной",
                "сенсацион",

            ]


            blocked = False


            for word in forbidden:

                if word in sentence_lower:

                    logger.warning(
                        "Removed hallucination phrase: %s",
                        sentence
                    )

                    removed += 1
                    blocked = True
                    break


            if blocked:
                continue



            # если предложение не имеет связи
            # с исходными фактами

            keywords = [
                w for w in re.findall(
                    r'[а-яa-z]{5,}',
                    sentence_lower
                )
            ]


            matches = sum(
                1
                for word in keywords
                if word in source_lower
            )


            # Sprint 8.5 fix: проверка keywords ОТКЛЮЧЕНА
            # LLM генерирует вовлекающие вопросы которые не содержат фактов из source,
            # но важны для вовлечения аудитории. Quality контролируется EvaluatorJob.
            # Поэтому мы НЕ удаляем предложения только из-за отсутствия совпадений keywords.



            lines.append(
                sentence.strip()
            )



        logger.info(
            "FactGuard removed %s sentences",
            removed
        )


        result = " ".join(
            lines
        )


        return result.strip()
