"""
Validators для WritingEngine v2.

GrammarValidator: проверка качества текста (длина предложений, повторы, стоп-слова)
StyleValidator: проверка соответствия платформенным требованиям (hook, эмодзи, структура)
"""
import re
import logging
from typing import List, Dict, Any
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Проблема, найденная валидатором."""
    category: str  # "grammar" | "style"
    severity: str  # "error" | "warning" | "info"
    message: str
    suggestion: str


class GrammarValidator:
    """
    Проверяет грамматическое качество текста:
    - Длина предложений (слишком длинные трудно читать)
    - Повторы слов подряд (тавтология)
    - Стоп-слова (вода, канцеляризмы)
    - Соотношение знаков препинания
    """
    
    def __init__(self):
        self.max_sentence_length = 150  # символов
        self.max_word_repeats = 3  # слово может повторяться максимум N раз в абзаце
        
        # Канцеляризмы и вода (русский)
        self.stop_words = [
            "является", "осуществляется", "данный", "указанный", "вышеуказанный",
            "в настоящее время", "на сегодняшний день", "в рамках", "в целях",
            "соответственно", "таким образом", "следовательно", "безусловно",
            "достаточно", "определенный", "некий", "какой-либо"
        ]
    
    def validate(self, text: str) -> List[ValidationIssue]:
        """Проверяет текст на грамматические проблемы."""
        issues = []
        
        if not text or not text.strip():
            return issues
        
        # Разбиваем на предложения
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 1. Проверка длины предложений
        long_sentences = [s for s in sentences if len(s) > self.max_sentence_length]
        if long_sentences:
            issues.append(ValidationIssue(
                category="grammar",
                severity="warning",
                message=f"Найдено {len(long_sentences)} слишком длинных предложений (>{self.max_sentence_length} символов)",
                suggestion="Разбейте длинные предложения на более короткие для лучшей читаемости"
            ))
        
        # 2. Проверка повторов слов в каждом абзаце
        paragraphs = text.split('\n\n')
        for para_idx, paragraph in enumerate(paragraphs):
            words = re.findall(r'\b\w+\b', paragraph.lower())
            word_counts = {}
            for word in words:
                if len(word) > 4:  # игнорируем короткие слова
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            repeated_words = {w: c for w, c in word_counts.items() if c > self.max_word_repeats}
            if repeated_words:
                word_list = ", ".join([f"'{w}' ({c} раз)" for w, c in list(repeated_words.items())[:3]])
                issues.append(ValidationIssue(
                    category="grammar",
                    severity="info",
                    message=f"В абзаце {para_idx + 1} есть повторы слов: {word_list}",
                    suggestion="Используйте синонимы для разнообразия"
                ))
        
        # 3. Проверка стоп-слов (канцеляризмы)
        text_lower = text.lower()
        found_stop_words = [word for word in self.stop_words if word in text_lower]
        if found_stop_words:
            issues.append(ValidationIssue(
                category="grammar",
                severity="warning",
                message=f"Найдено {len(found_stop_words)} канцеляризмов: {', '.join(found_stop_words[:5])}",
                suggestion="Замените канцеляризмы на более простые выражения"
            ))
        
        # 4. Проверка соотношения знаков препинания (слишком много восклицаний = кликбейт)
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            issues.append(ValidationIssue(
                category="grammar",
                severity="warning",
                message=f"Слишком много восклицательных знаков: {exclamation_count}",
                suggestion="Умеренное использование знаков препинания повышает доверие"
            ))
        
        return issues


class StyleValidator:
    """
    Проверяет соответствие стиля платформенным требованиям:
    - Hook в начале (цепляющий заголовок/вопрос)
    - Эмодзи (количество зависит от платформы)
    - Структура абзацев
    - Финальный вопрос для вовлечения
    """
    
    PLATFORM_RULES = {
        "telegram": {
            "min_paragraphs": 2,
            "max_paragraphs": 5,
            "min_emojis": 1,
            "max_emojis": 3,
            "require_hook": True,
            "require_final_question": True,
            "min_length": 300,
            "max_length": 1200
        },
        "vk": {
            "min_paragraphs": 3,
            "max_paragraphs": 10,
            "min_emojis": 2,
            "max_emojis": 8,
            "require_hook": True,
            "require_final_question": False,
            "min_length": 500,
            "max_length": 2500
        },
        "dzen": {
            "min_paragraphs": 5,
            "max_paragraphs": 15,
            "min_emojis": 0,
            "max_emojis": 5,
            "require_hook": True,
            "require_final_question": False,
            "min_length": 1500,
            "max_length": 5000
        },
        "youtube": {
            "min_paragraphs": 2,
            "max_paragraphs": 8,
            "min_emojis": 1,
            "max_emojis": 10,
            "require_hook": True,
            "require_final_question": True,
            "min_length": 400,
            "max_length": 2000
        }
    }
    
    def validate(self, text: str, platform: str = "telegram") -> List[ValidationIssue]:
        """Проверяет текст на соответствие стилю платформы."""
        issues = []
        
        if not text or not text.strip():
            return issues
        
        rules = self.PLATFORM_RULES.get(platform, self.PLATFORM_RULES["telegram"])
        
        # 1. Проверка длины
        text_length = len(text)
        if text_length < rules["min_length"]:
            issues.append(ValidationIssue(
                category="style",
                severity="warning",
                message=f"Текст слишком короткий для {platform}: {text_length} символов (мин {rules['min_length']})",
                suggestion=f"Увеличьте объём до {rules['min_length']}-{rules['max_length']} символов"
            ))
        elif text_length > rules["max_length"]:
            issues.append(ValidationIssue(
                category="style",
                severity="warning",
                message=f"Текст слишком длинный для {platform}: {text_length} символов (макс {rules['max_length']})",
                suggestion=f"Сократите до {rules['max_length']} символов"
            ))
        
        # 2. Проверка структуры абзацев
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) < rules["min_paragraphs"]:
            issues.append(ValidationIssue(
                category="style",
                severity="warning",
                message=f"Слишком мало абзацев: {len(paragraphs)} (мин {rules['min_paragraphs']})",
                suggestion="Разбейте текст на больше абзацев для лучшей читаемости"
            ))
        elif len(paragraphs) > rules["max_paragraphs"]:
            issues.append(ValidationIssue(
                category="style",
                severity="info",
                message=f"Много абзацев: {len(paragraphs)} (макс {rules['max_paragraphs']})",
                suggestion="Объедините короткие абзацы"
            ))
        
        # 3. Проверка эмодзи
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0]')
        emojis = emoji_pattern.findall(text)
        emoji_count = len(emojis)
        
        if emoji_count < rules["min_emojis"]:
            issues.append(ValidationIssue(
                category="style",
                severity="info",
                message=f"Мало эмодзи: {emoji_count} (мин {rules['min_emojis']})",
                suggestion="Добавьте эмодзи для визуального акцента"
            ))
        elif emoji_count > rules["max_emojis"]:
            issues.append(ValidationIssue(
                category="style",
                severity="warning",
                message=f"Слишком много эмодзи: {emoji_count} (макс {rules['max_emojis']})",
                suggestion="Уменьшите количество эмодзи для более профессионального вида"
            ))
        
        # 4. Проверка hook (цепляющее начало)
        if rules["require_hook"]:
            first_line = paragraphs[0] if paragraphs else ""
            has_hook = (
                '?' in first_line or  # вопрос
                '!' in first_line or  # восклицание
                any(word in first_line.lower() for word in ['новое', 'прорыв', 'революция', 'важно', 'срочно'])
            )
            if not has_hook:
                issues.append(ValidationIssue(
                    category="style",
                    severity="warning",
                    message="Отсутствует hook (цепляющее начало)",
                    suggestion="Начните с вопроса, восклицания или интригующего утверждения"
                ))
        
        # 5. Проверка финального вопроса для вовлечения
        if rules["require_final_question"]:
            last_paragraph = paragraphs[-1] if paragraphs else ""
            has_question = '?' in last_paragraph
            if not has_question:
                issues.append(ValidationIssue(
                    category="style",
                    severity="warning",
                    message="Отсутствует финальный вопрос для вовлечения аудитории",
                    suggestion="Завершите пост вопросом к читателям для повышения engagement"
                ))
        
        return issues


# Convenience function for quick validation
def validate_content(text: str, platform: str = "telegram") -> Dict[str, Any]:
    """
    Быстрая валидация контента всеми валидаторами.
    Возвращает словарь с результатами.
    """
    grammar_validator = GrammarValidator()
    style_validator = StyleValidator()
    
    grammar_issues = grammar_validator.validate(text)
    style_issues = style_validator.validate(text, platform)
    
    all_issues = grammar_issues + style_issues
    
    return {
        "is_valid": len([i for i in all_issues if i.severity == "error"]) == 0,
        "issues": all_issues,
        "summary": {
            "errors": len([i for i in all_issues if i.severity == "error"]),
            "warnings": len([i for i in all_issues if i.severity == "warning"]),
            "info": len([i for i in all_issues if i.severity == "info"])
        }
    }