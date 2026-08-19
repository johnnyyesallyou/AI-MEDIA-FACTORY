"""Image Validator - проверка качества изображений."""
import logging
from typing import Tuple
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


class ImageValidator:
    """
    Проверяет качество изображений.
    
    Критерии:
    - Минимальный размер: 512x512
    - Соотношение сторон: 0.5-2.0 (не слишком вытянутое)
    - Цветовой баланс: не полностью чёрное/белое
    
    Sprint 21: Smart Image Acquisition
    """

    MIN_SIZE = (512, 512)
    ASPECT_RATIO_MIN = 0.5
    ASPECT_RATIO_MAX = 2.0

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate(self, image_data: bytes) -> Tuple[bool, str]:
        """
        Проверяет качество изображения.
        
        Args:
            image_data: Байты изображения
        
        Returns:
            (is_valid, reason)
        """
        try:
            img = Image.open(BytesIO(image_data))
            width, height = img.size
            
            # 1. Минимальный размер
            if width < self.MIN_SIZE[0] or height < self.MIN_SIZE[1]:
                return False, f"Too small: {width}x{height} < {self.MIN_SIZE}"
            
            # 2. Соотношение сторон
            aspect_ratio = width / height
            if aspect_ratio < self.ASPECT_RATIO_MIN or aspect_ratio > self.ASPECT_RATIO_MAX:
                return False, f"Bad aspect ratio: {aspect_ratio:.2f}"
            
            # 3. Цветовой баланс (проверяем среднюю яркость)
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            pixels = list(img.getdata())
            if not pixels:
                return False, "Empty image"
            
            avg_brightness = sum(sum(p) / 3 for p in pixels) / len(pixels)
            
            if avg_brightness < 20:
                return False, f"Too dark: brightness={avg_brightness:.1f}"
            if avg_brightness > 235:
                return False, f"Too bright: brightness={avg_brightness:.1f}"
            
            return True, "OK"
        
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False, f"Error: {type(e).__name__}"