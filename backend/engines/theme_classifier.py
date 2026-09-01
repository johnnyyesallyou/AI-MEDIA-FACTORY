"""Sprint 68.1: Theme Classifier — LLM-based channel theme analysis."""
import json
import logging
import os
from typing import Dict, Any, Optional

import requests

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


class ThemeClassifier:
    """
    Анализирует описание канала и классифицирует:
    - theme (general category: technology, entertainment, education, etc)
    - niche (specific subcategory: ai, manga, gaming, etc)
    - archetype (news/releases/educational/viral/reviews/community/aggregator)
    - tone (informative/casual/analytical/humorous)
    - risk_level (low/medium/high)
    """
    
    CLASSIFICATION_PROMPT = """You are an expert at analyzing channel descriptions and classifying them for content automation.

Given a channel description, return a JSON object with:
- theme: general category (technology, entertainment, education, business, lifestyle, science, health, finance, etc)
- niche: specific subcategory (ai, gaming, manga, anime, movies, fitness, cooking, etc)
- archetype: one of [news, releases, educational, entertainment, viral, reviews, community, aggregator]
- tone: one of [informative, casual, analytical, humorous]
- risk_level: one of [low, medium, high]

Risk levels:
- low: entertainment, gaming, movies, memes, anime, manga
- medium: technology, science, business, education, reviews
- high: finance, crypto, medicine, nutrition, psychology, health advice

Examples:
"Канал про искусственный интеллект и нейросети" → {"theme": "technology", "niche": "ai", "archetype": "news", "tone": "informative", "risk_level": "medium"}
"Хочу канал про смешных котов" → {"theme": "entertainment", "niche": "cats", "archetype": "viral", "tone": "humorous", "risk_level": "low"}
"Новости манги и новые главы" → {"theme": "entertainment", "niche": "manga", "archetype": "releases", "tone": "informative", "risk_level": "low"}
"Канал про криптовалюты и трейдинг" → {"theme": "finance", "niche": "crypto", "archetype": "news", "tone": "analytical", "risk_level": "high"}

Channel description: {description}

Return ONLY valid JSON (no markdown, no explanation):
"""
    
    def classify(self, description: str) -> Dict[str, Any]:
        """Classify channel description using LLM."""
        logger.info(f"Classifying: {description[:50]}...")
        
        prompt = self.CLASSIFICATION_PROMPT.replace("{description}", description)
        
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
                timeout=60,
            )
            response.raise_for_status()
            
            result = response.json()
            llm_response = result.get("response", "")
            
            # Parse JSON from LLM response
            try:
                classification = json.loads(llm_response)
            except json.JSONDecodeError:
                logger.error(f"LLM returned invalid JSON: {llm_response[:200]}")
                return self._fallback_classification(description)
            
            # Validate required fields
            required = ["theme", "niche", "archetype", "tone", "risk_level"]
            for field in required:
                if field not in classification:
                    logger.warning(f"Missing field: {field}")
                    return self._fallback_classification(description)
            
            logger.info(f"Classification: {classification}")
            return classification
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM request failed: {e}")
            return self._fallback_classification(description)
    
    def _fallback_classification(self, description: str) -> Dict[str, Any]:
        """Fallback if LLM unavailable."""
        desc_lower = description.lower()
        
        # Keyword-based fallback
        if any(kw in desc_lower for kw in ["crypto", "крипт", "трейдинг", "биржа"]):
            return {"theme": "finance", "niche": "crypto", "archetype": "news", "tone": "analytical", "risk_level": "high"}
        if any(kw in desc_lower for kw in ["medicine", "медицин", "лечение", "здоровье"]):
            return {"theme": "health", "niche": "medicine", "archetype": "educational", "tone": "informative", "risk_level": "high"}
        if any(kw in desc_lower for kw in ["ai", "ии", "нейросет", "machine learning"]):
            return {"theme": "technology", "niche": "ai", "archetype": "news", "tone": "informative", "risk_level": "medium"}
        if any(kw in desc_lower for kw in ["manga", "манг", "anime", "аним"]):
            return {"theme": "entertainment", "niche": "manga", "archetype": "releases", "tone": "informative", "risk_level": "low"}
        if any(kw in desc_lower for kw in ["game", "игр", "gaming"]):
            return {"theme": "entertainment", "niche": "gaming", "archetype": "news", "tone": "casual", "risk_level": "low"}
        if any(kw in desc_lower for kw in ["news", "новост"]):
            return {"theme": "general", "niche": "news", "archetype": "news", "tone": "informative", "risk_level": "medium"}
        
        # Default
        return {"theme": "general", "niche": "misc", "archetype": "news", "tone": "informative", "risk_level": "medium"}