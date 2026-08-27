"""Channel Context - Sprint 57.

Загружает контекст канала: историю постов + learnings.
Используется Writing Engine для учёта темы и паттернов.
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ChannelContext:
    """
    Контекст канала для ИИ.
    Собирает всю информацию о канале и его истории.
    """
    
    def __init__(self, channel, db_session, include_history: int = 10):
        self.channel = channel
        self.db = db_session
        self.recent_posts = []
        self.learnings = []
        
        self._load_history(include_history)
        self._load_learnings()
    
    def _load_history(self, limit: int):
        """Загрузить последние посты"""
        from core.models.post_history_orm import PostHistoryORM
        
        try:
            self.recent_posts = self.db.query(PostHistoryORM)\
                .filter_by(channel_id=self.channel.id)\
                .order_by(PostHistoryORM.posted_at.desc())\
                .limit(limit)\
                .all()
            logger.debug(f"Loaded {len(self.recent_posts)} recent posts for channel {self.channel.id}")
        except Exception as e:
            logger.warning(f"Could not load history: {e}")
            self.recent_posts = []
    
    def _load_learnings(self):
        """Загрузить learnings - что работает на этом канале"""
        from core.models.post_history_orm import ChannelLearningsORM
        
        try:
            self.learnings = self.db.query(ChannelLearningsORM)\
                .filter_by(channel_id=self.channel.id)\
                .order_by(ChannelLearningsORM.score.desc())\
                .all()
            logger.debug(f"Loaded {len(self.learnings)} learnings for channel {self.channel.id}")
        except Exception as e:
            logger.warning(f"Could not load learnings: {e}")
            self.learnings = []
    
    def to_prompt_context(self) -> Dict:
        """Преобразовать контекст в словарь для промпта"""
        recent_texts = [p.text[:100] for p in self.recent_posts if p.text]
        patterns = [l.pattern for l in self.learnings if l.score > 0.6]
        
        # Извлекаем content_type и topic из content_profile
        content_profile = getattr(self.channel, 'content_profile', {}) or {}
        
        return {
            "platform": self.channel.platform,
            "channel_name": self.channel.name,
            "theme": self.channel.description or "General",
            "language": getattr(self.channel, 'language_publish', None) or "ru",
            "content_type": content_profile.get("content_type", "unknown"),
            "topic": content_profile.get("topic", "general"),
            "recent_posts_summary": " | ".join(recent_texts[:3]),
            "working_patterns": patterns,
            "audience": self._infer_audience(),
            "style": getattr(self.channel, 'style_profile', None) or "minimal"
        }
    
    def _infer_audience(self) -> str:
        """Определить аудиторию на основе названия и learnings"""
        name_lower = (self.channel.name or "").lower()
        
        if any(word in name_lower for word in ['tech', 'code', 'dev', 'python', 'js', 'it', 'технолог', 'программ']):
            return "Software engineers and developers"
        if any(word in name_lower for word in ['бизнес', 'финанс', 'крипто', 'трейд', 'business']):
            return "Business and finance professionals"
        if any(word in name_lower for word in ['спорт', 'gym', 'fitness', 'sport']):
            return "Sports and fitness enthusiasts"
        if any(word in name_lower for word in ['манга', 'manga', 'аниме', 'anime']):
            return "Manga and anime fans"
        if any(word in name_lower for word in ['новост', 'news']):
            return "News readers"
        
        return "General audience"
    
    def get_best_patterns(self, min_score: float = 0.7) -> List[str]:
        """Получить только лучшие паттерны"""
        return [l.pattern for l in self.learnings if l.score >= min_score]
    
    def get_video_preference(self) -> str:
        """Определить предпочтение: реальное vs генерированное видео"""
        video_learnings = [
            l for l in self.learnings 
            if 'video' in l.pattern.lower()
        ]
        
        if not video_learnings:
            return "auto"
        
        # Находим паттерны с "real" и "generated"
        real_scores = [
            l.score for l in video_learnings 
            if 'real' in l.pattern.lower() or 'pexels' in l.pattern.lower()
        ]
        gen_scores = [
            l.score for l in video_learnings 
            if 'generated' in l.pattern.lower() or 'runway' in l.pattern.lower()
        ]
        
        avg_real = sum(real_scores) / len(real_scores) if real_scores else 0.5
        avg_gen = sum(gen_scores) / len(gen_scores) if gen_scores else 0.5
        
        return "generated" if avg_gen > avg_real else "real"