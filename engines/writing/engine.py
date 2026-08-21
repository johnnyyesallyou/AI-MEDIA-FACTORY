"""
WritingEngine v2 — Production Pipeline.

Архитектура:
  Brief
    ↓
  [1] Model Selector (автовыбор модели по типу контента)
    ↓
  [2] Prompt Builder (SYSTEM + STYLE + PLATFORM + <FACTS> + RULES)
    ↓
  [3] LLM (Ollama)
    ↓
  [4] Fact Checker (FactGuard)
    ↓
  [5] Grammar Validator (длина предложений, повторы, стоп-слова)
    ↓
  [6] Style Validator (hook, эмодзи, структура)
    ↓
  [7] Post Processor (OutputGuard)
    ↓
  ContentDraft (+ validation_issues)
"""
import asyncio
import os
import logging
import requests
import time
from typing import Dict, Any, Optional

from .models import ContentBrief, ContentDraft, ValidationIssue
from .prompt_builder import PromptBuilder
from .fact_guard import FactGuard
from .output_guard import OutputGuard
from .model_selector import ModelSelector
from .validators import GrammarValidator, StyleValidator
from .styles.profiles import TELEGRAM_AI_EXPERT


logger = logging.getLogger(__name__)


class WritingEngine:
    """Production Pipeline для генерации контента."""
    
    def __init__(self, base_url: str = None, override_model: str = None):
        # Читаем OLLAMA_URL из env (как в EvaluatorEngine)
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
        self.override_model = override_model
        self.model_selector = ModelSelector()
    
    async def generate(self, brief: ContentBrief, style_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Генерирует контент по брифу через полный pipeline.
        
        Returns:
            Dict с ключами: generated_text, draft (ContentDraft), model_used
        """
        style_profile = style_profile or TELEGRAM_AI_EXPERT
        
        # [1] Model Selector
        selected_model = self.model_selector.select_model(brief, self.override_model)
        logger.info(f"[1/7] Model selected: {selected_model}")
        
        # [2] Prompt Builder
        prompt_builder = PromptBuilder(style_profile)
        user_prompt = prompt_builder.build(brief)
        system_prompt = self._build_system_prompt(style_profile)
        logger.info(f"[2/7] Prompt built ({len(user_prompt)} chars)")
        
        # [3] LLM
        llm_response = await asyncio.to_thread(
            self._call_llm,
            system_prompt,
            user_prompt,
            selected_model
        )
        if not llm_response:
            raise RuntimeError("LLM failed to generate response")
        generated_text = llm_response.strip()
        logger.info(f"[3/7] LLM generated {len(generated_text)} chars")
        
        # [4] Fact Checker
        fact_guard = FactGuard()
        facts = brief.key_facts if brief.key_facts else []
        if facts:
            text_before = len(generated_text)
            generated_text = fact_guard.clean(generated_text, facts)
            fact_check_passed = len(generated_text) >= text_before * 0.7  # если удалили < 30% — ОК
            logger.info(f"[4/7] Fact check: {text_before} -> {len(generated_text)} chars (passed={fact_check_passed})")
        else:
            fact_check_passed = True
            logger.info(f"[4/7] Fact check: skipped (no facts)")
        
        # [5] Grammar Validator
        grammar_validator = GrammarValidator()
        grammar_issues = grammar_validator.validate(generated_text)
        logger.info(f"[5/7] Grammar validation: {len(grammar_issues)} issues found")
        
        # [6] Style Validator
        style_validator = StyleValidator()
        platform = brief.platform or "telegram"
        style_issues = style_validator.validate(generated_text, platform)
        logger.info(f"[6/7] Style validation: {len(style_issues)} issues found")
        
        # [7] Post Processor (OutputGuard)
        output_guard = OutputGuard()
        generated_text = output_guard.clean(generated_text)
        logger.info(f"[7/7] Post-processed: {len(generated_text)} chars")
        
        # Собираем все issues
        all_issues = []
        for issue in grammar_issues + style_issues:
            all_issues.append(ValidationIssue(
                category=issue.category,
                severity=issue.severity,
                message=issue.message,
                suggestion=issue.suggestion
            ))
        
        # Создаём ContentDraft
        draft = ContentDraft(
            brief_id=brief.id,
            title=brief.topic[:100],
            body=generated_text,
            model_used=selected_model,
            tokens_input=len(user_prompt.split()),
            tokens_output=len(generated_text.split()),
            platform=platform,
            validation_issues=all_issues,
            fact_check_passed=fact_check_passed
        )
        
        # Возвращаем результат (обратно совместимо)
        return {
            "generated_text": generated_text,
            "model_used": selected_model,
            "draft": draft,
            "validation_summary": {
                "errors": len([i for i in all_issues if i.severity == "error"]),
                "warnings": len([i for i in all_issues if i.severity == "warning"]),
                "info": len([i for i in all_issues if i.severity == "info"])
            }
        }
    
    def _build_system_prompt(self, style_profile: Dict[str, Any]) -> str:
        """Строит системный промпт."""
        return f"""Ты — профессиональный писатель для платформы {style_profile.get('channel', 'telegram')}.

СТИЛЬ:
{style_profile.get('tone', 'Профессиональный')}

АУДИТОРИЯ:
{style_profile.get('audience', 'IT-специалисты')}

ФОРМАТ:
{style_profile.get('format', 'Заголовок + 2-3 абзаца')}

ЭМОДЗИ:
{style_profile.get('emoji_usage', 'Умеренное')}

ЗАПРЕЩЕНО:
{', '.join(style_profile.get('forbidden', []))}

ПРИМЕР:
{style_profile.get('example', '')}

ВАЖНО:
- Используй ТОЛЬКО информацию из <FACTS>
- Не выдумывай факты, цифры, имена
- Не добавляй служебные блоки
- Начни сразу с текста поста"""
    
    def _call_llm(self, system_prompt: str, user_prompt: str, model: str) -> str:
        """Вызывает LLM (синхронно, для asyncio.to_thread)."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1024,
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise