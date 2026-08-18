"""Image Acquisition Policy - Sprint 33.

Policy-driven выбор источника изображения.

Правила:
  MANGA  → только реальная обложка из Knowledge Layer (fallback: none)
  ANIME  → только реальный key visual из AniList (fallback: none)
  NEWS   → og:image (реальная картинка новости)
            ↓ если нет
          AI fallback ТОЛЬКО если image_policy.fallback == "ai_generated"
            ↓
          ImageEngine (Pollinations) + опциональный ImageValidator

ImageEngine больше НЕ обязательный генератор — только controlled fallback.
"""
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AcquisitionResult:
    """Результат приобретения изображения."""
    url: Optional[str]
    source: str  # "real" | "ai" | "none"
    prompt: Optional[str] = None
    validated: bool = False


class ImageAcquisitionPolicy:
    """Policy-driven image acquisition."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._image_engine = None
        self._validator = None

    @property
    def image_engine(self):
        """Lazy init ImageEngine (дорогой)."""
        if self._image_engine is None:
            from engines.image.engine import ImageEngine
            self._image_engine = ImageEngine()
        return self._image_engine

    @property
    def validator(self):
        """Lazy init ImageValidator (Ollama)."""
        if self._validator is None:
            from engines.image_validator.engine import ImageValidatorEngine
            self._validator = ImageValidatorEngine()
        return self._validator

    def acquire(
        self,
        content,
        real_url: Optional[str],
        profile: dict,
    ) -> AcquisitionResult:
        """
        Policy-driven приобретение изображения.

        Args:
            content: ContentORM
            real_url: валидный реальный URL (cover/og:image) или None
            profile: channel profile

        Returns:
            AcquisitionResult
        """
        image_policy = profile.get("image_policy", {})
        content_type = profile.get("content_type", "news")
        fallback = image_policy.get("fallback", "none")

        # 1. Реальная картинка — всегда приоритет
        if real_url:
            return AcquisitionResult(url=real_url, source="real")

        # 2. AI fallback — ТОЛЬКО для news и ТОЛЬКО если разрешено профилем
        if content_type == "news" and fallback == "ai_generated":
            return self._ai_fallback(content, image_policy)

        # 3. Нет картинки (manga/anime без cover → text post, НЕ AI!)
        self.logger.info(
            f"No image for {content_type} (fallback={fallback}) → text post"
        )
        return AcquisitionResult(url=None, source="none")

    def _ai_fallback(self, content, image_policy: dict) -> AcquisitionResult:
        """AI-генерация как controlled fallback для news."""
        try:
            style = image_policy.get("style", "news")

            result = self.image_engine.generate(
                headline=content.headline or "",
                text=content.draft_text or "",
                platform="telegram",
                style=style,
            )

            ai_url = result.get("image_url")
            prompt = result.get("prompt")

            if not ai_url:
                self.logger.warning("AI fallback: no image_url generated")
                return AcquisitionResult(url=None, source="none")

            validated = False

            # Опциональная валидация через LLM Vision (если включена и Ollama доступен)
            if image_policy.get("validate_with_llm", False):
                try:
                    v = self.validator.validate(
                        image_url=ai_url,
                        original_prompt=prompt or "",
                        context=content.headline or "",
                    )
                    validated = bool(v.get("passed"))
                    self.logger.info(
                        f"AI image validation: score={v.get('overall_score')}, passed={validated}"
                    )
                    if not validated:
                        self.logger.warning(
                            f"AI image rejected: {v.get('feedback', '')[:100]}"
                        )
                        return AcquisitionResult(url=None, source="none")
                except Exception as e:
                    self.logger.warning(f"AI validation skipped: {e}")

            self.logger.info(f"AI fallback used: {ai_url[:80]}")
            return AcquisitionResult(
                url=ai_url,
                source="ai",
                prompt=prompt,
                validated=validated,
            )

        except Exception as e:
            self.logger.warning(f"AI fallback failed: {e}")
            return AcquisitionResult(url=None, source="none")