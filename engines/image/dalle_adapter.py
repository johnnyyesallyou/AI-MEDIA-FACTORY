"""DALL-E Adapter - Sprint 38.

AI-генерация изображений через OpenAI DALL-E.
Требует: OPENAI_API_KEY
Без ключа — gracefully деградирует (available=False).
"""
import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class DALLEAdapter:
    """Генерация изображений через DALL-E 3."""

    API_URL = "https://api.openai.com/v1/images/generations"
    TIMEOUT = 60

    def __init__(self, api_key: Optional[str] = None, model: str = "dall-e-3"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def generate(
        self,
        prompt: str,
        size: str = "1792x1024",
        style: str = "natural",
    ) -> Optional[str]:
        """Генерирует изображение. Возвращает URL или None."""
        if not self.available:
            return None

        try:
            r = requests.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "n": 1,
                    "size": size,
                    "style": style,
                },
                timeout=self.TIMEOUT,
            )

            if r.status_code != 200:
                self.logger.warning(f"DALL-E failed: {r.status_code} {r.text[:100]}")
                return None

            data = r.json()
            url = data.get("data", [{}])[0].get("url")
            if url:
                self.logger.info(f"DALL-E generated: {prompt[:40]}")
            return url

        except Exception as e:
            self.logger.warning(f"DALL-E error: {e}")
            return None