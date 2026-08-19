"""ComfyUI Engine - локальная генерация изображений через ComfyUI API."""
import logging
import requests
import time
import json
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ComfyUIEngine:
    """
    Sprint 13: Генерация изображений через локальный ComfyUI.
    Заменяет Pollinations AI для лучшего качества и контроля.
    
    Требует запущенный ComfyUI контейнер на http://comfyui:8188
    """
    
    def __init__(self, base_url: str = "http://comfyui:8188"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 300  # 5 минут для генерации
        
    def _check_health(self) -> bool:
        """Проверяет доступность ComfyUI."""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"ComfyUI health check failed: {e}")
            return False
    
    def _queue_prompt(self, workflow: Dict[str, Any]) -> Optional[str]:
        """Отправляет workflow в очередь ComfyUI."""
        try:
            payload = {"prompt": workflow}
            response = requests.post(
                f"{self.base_url}/prompt",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            prompt_id = data.get("prompt_id")
            logger.info(f"ComfyUI: Queued prompt {prompt_id}")
            return prompt_id
        except Exception as e:
            logger.error(f"ComfyUI queue_prompt failed: {e}")
            return None
    
    def _wait_for_completion(self, prompt_id: str, poll_interval: int = 2) -> bool:
        """Ждёт завершения генерации."""
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                response = requests.get(
                    f"{self.base_url}/history/{prompt_id}",
                    timeout=10
                )
                if response.status_code == 200:
                    history = response.json()
                    if prompt_id in history:
                        logger.info(f"ComfyUI: Prompt {prompt_id} completed")
                        return True
                time.sleep(poll_interval)
            except Exception as e:
                logger.warning(f"ComfyUI polling error: {e}")
                time.sleep(poll_interval)
        
        logger.error(f"ComfyUI: Timeout waiting for {prompt_id}")
        return False
    
    def _get_output_image(self, prompt_id: str) -> Optional[str]:
        """Получает путь к сгенерированному изображению."""
        try:
            response = requests.get(
                f"{self.base_url}/history/{prompt_id}",
                timeout=10
            )
            response.raise_for_status()
            history = response.json()
            
            if prompt_id not in history:
                return None
            
            outputs = history[prompt_id].get("outputs", {})
            for node_id, node_output in outputs.items():
                if "images" in node_output:
                    images = node_output["images"]
                    if images:
                        # Возвращаем путь к первому изображению
                        image = images[0]
                        filename = image.get("filename")
                        subfolder = image.get("subfolder", "")
                        image_type = image.get("type", "output")
                        return f"{image_type}/{subfolder}/{filename}".strip("/")
            
            return None
        except Exception as e:
            logger.error(f"ComfyUI get_output_image failed: {e}")
            return None
    
    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        model: str = "flux",
        steps: int = 20,
        cfg: float = 7.5,
        seed: int = -1
    ) -> Dict[str, Any]:
        """
        Генерирует изображение через ComfyUI.
        
        Args:
            prompt: Текстовый промпт
            negative_prompt: Негативный промпт
            width: Ширина изображения
            height: Высота изображения
            model: Модель (flux/sdxl)
            steps: Количество шагов sampling
            cfg: CFG scale
            seed: Seed (-1 для случайного)
        
        Returns:
            {"image_path": str, "prompt": str, "model": str}
        """
        try:
            # Проверяем доступность ComfyUI
            if not self._check_health():
                logger.error("ComfyUI is not available")
                return self._fallback_to_pollinations(prompt, width, height)
            
            # Базовый workflow для txt2img
            workflow = {
                "3": {
                    "class_type": "KSampler",
                    "inputs": {
                        "seed": seed if seed != -1 else int(time.time()),
                        "steps": steps,
                        "cfg": cfg,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": 1.0,
                        "model": ["4", 0],
                        "positive": ["6", 0],
                        "negative": ["7", 0],
                        "latent_image": ["5", 0]
                    }
                },
                "4": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {
                        "ckpt_name": f"{model}.safetensors"
                    }
                },
                "5": {
                    "class_type": "EmptyLatentImage",
                    "inputs": {
                        "width": width,
                        "height": height,
                        "batch_size": 1
                    }
                },
                "6": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {
                        "text": prompt,
                        "clip": ["4", 1]
                    }
                },
                "7": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {
                        "text": negative_prompt,
                        "clip": ["4", 1]
                    }
                },
                "8": {
                    "class_type": "VAEDecode",
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["4", 2]
                    }
                },
                "9": {
                    "class_type": "SaveImage",
                    "inputs": {
                        "images": ["8", 0],
                        "filename_prefix": "amf"
                    }
                }
            }
            
            # Отправляем в очередь
            prompt_id = self._queue_prompt(workflow)
            if not prompt_id:
                return self._fallback_to_pollinations(prompt, width, height)
            
            # Ждём завершения
            if not self._wait_for_completion(prompt_id):
                return self._fallback_to_pollinations(prompt, width, height)
            
            # Получаем путь к изображению
            image_path = self._get_output_image(prompt_id)
            if not image_path:
                return self._fallback_to_pollinations(prompt, width, height)
            
            logger.info(f"ComfyUI: Generated {image_path}")
            return {
                "image_path": image_path,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "model": model,
                "width": width,
                "height": height,
                "source": "comfyui"
            }
        
        except Exception as e:
            logger.exception(f"ComfyUI generation failed: {e}")
            return self._fallback_to_pollinations(prompt, width, height)
    
    def _fallback_to_pollinations(self, prompt: str, width: int, height: int) -> Dict[str, Any]:
        """Fallback на Pollinations AI если ComfyUI недоступен."""
        logger.warning("Falling back to Pollinations AI")
        from engines.image.engine import ImageEngine
        
        image_engine = ImageEngine()
        result = image_engine.generate(
            headline=prompt,
            text="",
            platform="telegram",
            style="anime",
            width=width,
            height=height
        )
        
        result["source"] = "pollinations_fallback"
        return result
