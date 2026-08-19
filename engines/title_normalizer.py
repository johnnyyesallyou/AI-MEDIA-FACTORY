"""Title Normalizer - Sprint 23 (fixed).

Приводит названия манги к единому виду для дедупликации.

Правила:
1. lower case
2. Убираем пунктуацию (но сохраняем пробелы)
3. Схлопываем пробелы
4. Применяем известные RU->EN маппинги
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TitleNormalizer:
    """Нормализатор названий манги."""

    # Русские -> английские соответствия (упрощённые)
    RU_EN_MAPPING = {
        "ван пис": "one piece",
        "атака титанов": "attack on titan",
        "наруто": "naruto",
        "блич": "bleach",
        "токийский гуль": "tokyo ghoul",
        "тетрадь смерти": "death note",
        "человек бензопила": "chainsaw man",
        "моё геройское академия": "my hero academia",
    }

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def normalize(self, title: str) -> str:
        """
        Нормализует название:
        1. lower case
        2. удаляет пунктуацию (оставляя буквы, цифры, пробелы)
        3. схлопывает пробелы
        4. применяет известные маппинги
        """
        if not title:
            return ""

        # Lower case
        normalized = title.lower().strip()

        # Заменяем дефисы на пробелы
        normalized = normalized.replace("-", " ")

        # Убираем пунктуацию (кроме букв, цифр, пробелов)
        normalized = re.sub(r"[^\w\sа-яё]", "", normalized, flags=re.IGNORECASE | re.UNICODE)

        # Схлопываем пробелы
        normalized = re.sub(r"\s+", " ", normalized).strip()

        # Применяем известные маппинги
        if normalized in self.RU_EN_MAPPING:
            normalized = self.RU_EN_MAPPING[normalized]

        return normalized

    def is_same_title(self, title1: str, title2: str) -> bool:
        """Проверяет что два названия относятся к одной манге."""
        return self.normalize(title1) == self.normalize(title2)