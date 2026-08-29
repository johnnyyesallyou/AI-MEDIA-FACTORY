"""Media Policy - Sprint 60.5.

Определяет медиа-стратегию профиля канала.

Примеры:
  manga_releases:
    primary: cover (image из источника)
    video: false (манга не нужна с видео)
    
  anime_news:
    primary: key_visual (image)
    video_fallback: true (если нет key_visual, попробуем видео)
    
  tech_news:
    primary: video (Pixabay)
    fallback: source_image (если видео не найдено)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MediaPolicy:
    """Медиа-политика профиля канала."""
    
    primary: str  # 'video' | 'image' | 'none'
    source: str   # 'pixabay' | 'cover' | 'key_visual' | 'source_image' | 'none'
    fallback: Optional[str] = None  # 'image' | 'video' | 'none'
    video_fallback: bool = False  # использовать видео как fallback если primary не найден
    
    def should_fetch_video(self) -> bool:
        """Нужно ли вообще запрашивать видео."""
        return self.primary == 'video' or self.video_fallback or self.fallback == 'video'
    
    def should_fetch_image(self) -> bool:
        """Нужно ли вообще запрашивать картинку."""
        return self.primary == 'image' or self.fallback == 'image'


# Предустановленные политики
MEDIA_POLICIES = {
    # Манга: используем cover из источника, видео не нужно
    "manga_releases": MediaPolicy(
        primary="image",
        source="cover",
        video_fallback=False,
    ),
    
    # Anime: key_visual + опциональное видео
    "anime_news": MediaPolicy(
        primary="image",
        source="key_visual",
        video_fallback=True,
    ),
    
    # Tech news: приоритет видео, fallback на картинку из источника
    "tech_news": MediaPolicy(
        primary="video",
        source="pixabay",
        fallback="image",
    ),
    
    # AI news: приоритет видео
    "ai_news": MediaPolicy(
        primary="video",
        source="pixabay",
        fallback="image",
    ),
    
    # Общий профиль: сначала видео, потом картинка
    "general": MediaPolicy(
        primary="video",
        source="pixabay",
        fallback="image",
    ),
}


def get_media_policy(profile_key: str) -> MediaPolicy:
    """Получить media policy по ключу профиля."""
    return MEDIA_POLICIES.get(profile_key, MEDIA_POLICIES["general"])