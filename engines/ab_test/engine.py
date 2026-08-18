"""A/B Testing Engine - генерация и выбор лучшего варианта изображения."""
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests

from engines.comfyui.engine import ComfyUIEngine
from engines.image.engine import ImageEngine
from engines.image_validator.engine import ImageValidatorEngine

logger = logging.getLogger(__name__)


class ABTestEngine:
    """
    Sprint 13: Генерирует несколько вариантов изображений и выбирает лучший.
    
    Поддерживает два режима:
    1. ComfyUI (локальный) - если доступен
    2. Pollinations AI (fallback) - если ComfyUI недоступен
    
    ВАЖНО: A/B тесты работают АВТОНОМНО без сохранения в БД.
    Изображения сохраняются во временную директорию /app/assets/ab_test/
    
    Архитектура: NO database access (согласно Engineering Bible).
    """
    
    AB_TEST_DIR = "/app/assets/ab_test"
    
    def __init__(
        self,
        num_variants: int = 3,
        comfyui_url: str = "http://comfyui:8188"
    ):
        self.num_variants = num_variants
        self.comfyui_engine = ComfyUIEngine(base_url=comfyui_url)
        self.image_engine = ImageEngine()  # Pollinations fallback
        self.validator = ImageValidatorEngine()
        
        # Создаём директорию для A/B тестов
        self.ab_test_path = Path(self.AB_TEST_DIR)
        self.ab_test_path.mkdir(parents=True, exist_ok=True)
        
    def _download_image_direct(
        self, 
        url: str, 
        save_path: Path,
        timeout: int = 60,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Скачивает изображение напрямую без AssetManager и БД.
        
        Args:
            url: URL изображения
            save_path: Полный путь для сохранения файла
            timeout: Timeout для скачивания (увеличен до 60 сек)
            max_retries: Количество попыток
        
        Returns:
            Полный путь к файлу или None
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Download attempt {attempt+1}/{max_retries}: {url[:80]}...")
                
                response = requests.get(url, timeout=timeout, stream=True)
                response.raise_for_status()
                
                # Проверяем что это изображение
                content_type = response.headers.get("content-type", "")
                if "image" not in content_type and "octet-stream" not in content_type:
                    logger.warning(f"Unexpected content-type: {content_type}")
                
                # Сохраняем файл
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = save_path.stat().st_size
                logger.info(f"Image saved: {save_path} ({file_size} bytes)")
                
                # Валидация размера
                if file_size < 1024:
                    logger.warning(f"Image too small ({file_size} bytes), might be corrupted")
                    if attempt < max_retries - 1:
                        logger.info("Retrying...")
                        time.sleep(2 ** attempt)
                        continue
                    return None
                
                return str(save_path)
            
            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(f"Download timeout (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Download failed after {max_retries} attempts")
            
            except Exception as e:
                last_error = e
                logger.error(f"Failed to download image (attempt {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Download failed after {max_retries} attempts")
        
        return None
    
    def generate_variants(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        model: str = "flux",
        num_variants: int = None
    ) -> List[Dict[str, Any]]:
        """
        Генерирует несколько вариантов изображения.
        
        Returns:
            List of generated variants with scores
        """
        n = num_variants or self.num_variants
        variants = []
        
        # Проверяем доступен ли ComfyUI
        comfyui_available = self.comfyui_engine._check_health()
        source = "comfyui" if comfyui_available else "pollinations"
        
        logger.info(f"ABTest: Generating {n} variants using {source}")
        logger.info(f"Prompt: {prompt[:50]}...")
        
        # Создаём поддиректорию для этого теста
        test_id = f"test_{int(time.time())}"
        test_dir = self.ab_test_path / test_id
        test_dir.mkdir(exist_ok=True)
        logger.info(f"ABTest: Test directory: {test_dir}")
        
        for i in range(n):
            seed = int(time.time()) + i * 1000
            
            logger.info(f"ABTest: Generating variant {i+1}/{n} (seed={seed})")
            
            try:
                image_path = None
                image_url = None
                
                if comfyui_available:
                    # ComfyUI mode
                    result = self.comfyui_engine.generate(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        width=width,
                        height=height,
                        model=model,
                        seed=seed
                    )
                    
                    if not result or not result.get("image_path"):
                        logger.warning(f"ABTest: Variant {i+1} ComfyUI generation failed")
                        continue
                    
                    image_path = result["image_path"]
                    
                else:
                    # Pollinations fallback
                    result = self.image_engine.generate(
                        headline=prompt,
                        text="",
                        platform="telegram",
                        style="anime",
                        width=width,
                        height=height
                    )
                    
                    if not result or not result.get("image_url"):
                        logger.warning(f"ABTest: Variant {i+1} Pollinations generation failed")
                        continue
                    
                    image_url = result["image_url"]
                    
                    # ИСПРАВЛЕНО: Скачиваем прямо в test_dir
                    filename = f"variant_{i+1}_seed_{seed}.png"
                    save_path = test_dir / filename
                    
                    image_path = self._download_image_direct(
                        url=image_url,
                        save_path=save_path,
                        timeout=60,  # Увеличенный timeout
                        max_retries=3  # Retry логика
                    )
                    
                    if not image_path:
                        logger.warning(f"ABTest: Variant {i+1} download failed")
                        continue
                    
                    logger.info(f"ABTest: Downloaded variant {i+1} to {image_path}")
                
                # Создаём variant dict
                variant = {
                    "variant_id": i + 1,
                    "seed": seed,
                    "source": source,
                    "image_path": image_path,
                    "image_url": image_url,
                    "generation_time_ms": result.get("generation_time_ms", 0)
                }
                
                # Валидируем вариант
                logger.info(f"ABTest: Validating variant {i+1}...")
                validation = self.validator.validate(
                    image_path=image_path,
                    original_prompt=prompt,
                    context=f"Variant {i+1}"
                )
                
                variant["validation"] = validation
                variant["overall_score"] = validation["overall_score"]
                
                variants.append(variant)
                logger.info(
                    f"ABTest: Variant {i+1} scored {validation['overall_score']} "
                    f"(quality={validation['quality_score']}, "
                    f"prompt_match={validation['prompt_match']}, "
                    f"aesthetic={validation['aesthetic_score']})"
                )
            
            except Exception as e:
                logger.error(f"ABTest: Variant {i+1} failed: {e}")
        
        return variants
    
    def select_best(self, variants: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Выбирает лучший вариант по overall_score."""
        if not variants:
            logger.warning("ABTest: No variants to select from")
            return None
        
        sorted_variants = sorted(
            variants,
            key=lambda v: v.get("overall_score", 0),
            reverse=True
        )
        
        best = sorted_variants[0]
        logger.info(
            f"ABTest: Selected variant {best['variant_id']} "
            f"with score {best['overall_score']}"
        )
        
        return best
    
    def generate_and_select(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        model: str = "flux",
        num_variants: int = None
    ) -> Dict[str, Any]:
        """Полный цикл: генерация вариантов + выбор лучшего."""
        try:
            variants = self.generate_variants(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                model=model,
                num_variants=num_variants
            )
            
            if not variants:
                logger.error("ABTest: No variants generated")
                return {
                    "best_variant": None,
                    "all_variants": [],
                    "num_generated": 0,
                    "num_passed": 0,
                    "selection_reason": "No variants generated"
                }
            
            passed_variants = [v for v in variants if v["validation"]["passed"]]
            best = self.select_best(variants)
            
            result = {
                "best_variant": best,
                "all_variants": variants,
                "num_generated": len(variants),
                "num_passed": len(passed_variants),
                "selection_reason": f"Selected variant {best['variant_id']} with score {best['overall_score']}"
            }
            
            logger.info(
                f"ABTest: Generated {len(variants)} variants, "
                f"{len(passed_variants)} passed validation, "
                f"selected variant {best['variant_id']}"
            )
            
            return result
        
        except Exception as e:
            logger.exception(f"ABTest failed: {e}")
            return {
                "best_variant": None,
                "all_variants": [],
                "num_generated": 0,
                "num_passed": 0,
                "selection_reason": f"ABTest error: {str(e)}"
            }
