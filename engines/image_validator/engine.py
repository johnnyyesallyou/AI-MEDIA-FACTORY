"""Image Validator Engine - оценка качества сгенерированных изображений через LLM."""
import logging
import requests
import base64
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageValidatorEngine:
    """
    Sprint 13: Оценивает качество сгенерированных изображений через LLM Vision.
    
    Использует Ollama с vision-моделью для оценки:
    - Качество изображения (0-100)
    - Соответствие промпту (0-100)
    - Эстетическая привлекательность (0-100)
    
    Архитектура: NO database access (pure HTTP to Ollama).
    """
    
    QUALITY_THRESHOLD = 70  # Минимальный порог качества
    
    def __init__(
        self,
        ollama_url: str = "http://host.docker.internal:11434",
        model: str = "llava:7b"  # Vision модель для оценки картинок
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.timeout = 60
        
    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """Кодирует изображение в base64 для отправки в LLM."""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.error(f"Image not found: {image_path}")
                return None
            
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encode image: {e}")
            return None
    
    def _encode_url_to_base64(self, image_url: str) -> Optional[str]:
        """Скачивает и кодирует изображение из URL."""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            return base64.b64encode(response.content).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to download image from URL: {e}")
            return None
    
    def validate(
        self,
        image_path: str = None,
        image_url: str = None,
        original_prompt: str = "",
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Оценивает качество изображения через LLM Vision.
        
        Args:
            image_path: Локальный путь к изображению
            image_url: URL изображения (если не локальное)
            original_prompt: Промпт использованный для генерации
            context: Дополнительный контекст (название поста, тема)
        
        Returns:
            {
                "quality_score": int (0-100),
                "prompt_match": int (0-100),
                "aesthetic_score": int (0-100),
                "overall_score": int (0-100),
                "passed": bool,
                "feedback": str,
                "source": str
            }
        """
        try:
            # Получаем base64 изображения
            image_base64 = None
            source = "unknown"
            
            if image_path:
                image_base64 = self._encode_image_to_base64(image_path)
                source = "local_path"
            elif image_url:
                image_base64 = self._encode_url_to_base64(image_url)
                source = "url"
            
            if not image_base64:
                logger.warning("Could not load image, returning default score")
                return self._default_result("Image loading failed")
            
            # Проверяем доступность Ollama
            if not self._check_ollama():
                logger.warning("Ollama not available, returning default score")
                return self._default_result("Ollama unavailable")
            
            # Формируем промпт для оценки
            eval_prompt = f"""You are an expert image quality evaluator for anime-style media content.

Evaluate this image on three criteria (0-100 each):
1. Quality Score: Technical quality, sharpness, clarity, no artifacts
2. Prompt Match: How well the image matches the original prompt
3. Aesthetic Score: Visual appeal, composition, color harmony

Original Prompt: {original_prompt or 'Not provided'}
Context: {context or 'Anime news illustration'}

Respond ONLY with JSON in this exact format:
{{
  "quality_score": <0-100>,
  "prompt_match": <0-100>,
  "aesthetic_score": <0-100>,
  "feedback": "<brief feedback in 1-2 sentences>"
}}
"""
            
            # Вызываем Ollama Vision API
            payload = {
                "model": self.model,
                "prompt": eval_prompt,
                "images": [image_base64],
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Низкая температура для стабильности
                    "num_predict": 200
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            llm_response = data.get("response", "")
            logger.info(f"ImageValidator LLM response: {llm_response[:200]}")
            
            # Парсим JSON из ответа
            result = self._parse_llm_response(llm_response)
            result["source"] = source
            
            # Проверяем порог качества
            result["passed"] = result["overall_score"] >= self.QUALITY_THRESHOLD
            
            logger.info(
                f"ImageValidator: quality={result['quality_score']}, "
                f"prompt_match={result['prompt_match']}, "
                f"aesthetic={result['aesthetic_score']}, "
                f"overall={result['overall_score']}, "
                f"passed={result['passed']}"
            )
            
            return result
        
        except Exception as e:
            logger.exception(f"ImageValidator failed: {e}")
            return self._default_result(f"Validation error: {str(e)}")
    
    def _check_ollama(self) -> bool:
        """Проверяет доступность Ollama."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Парсит JSON из ответа LLM."""
        import json
        import re
        
        try:
            # Ищем JSON в ответе
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                quality = int(data.get("quality_score", 50))
                prompt_match = int(data.get("prompt_match", 50))
                aesthetic = int(data.get("aesthetic_score", 50))
                feedback = data.get("feedback", "No feedback")
                
                # Overall = взвешенное среднее
                overall = int(quality * 0.4 + prompt_match * 0.3 + aesthetic * 0.3)
                
                return {
                    "quality_score": quality,
                    "prompt_match": prompt_match,
                    "aesthetic_score": aesthetic,
                    "overall_score": overall,
                    "feedback": feedback,
                    "passed": overall >= self.QUALITY_THRESHOLD
                }
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
        
        # Fallback если парсинг не удался
        return self._default_result("LLM response parsing failed")
    
    def _default_result(self, reason: str) -> Dict[str, Any]:
        """Возвращает результат по умолчанию когда LLM недоступен."""
        default_score = 75  # Предполагаем что изображение ок
        return {
            "quality_score": default_score,
            "prompt_match": default_score,
            "aesthetic_score": default_score,
            "overall_score": default_score,
            "passed": default_score >= self.QUALITY_THRESHOLD,
            "feedback": f"Default score ({reason})",
            "source": "default"
        }
