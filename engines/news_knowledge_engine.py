"""News Knowledge Engine - Sprint 32.

Дедуплицирует новости по URL и создаёт NewsArticle в Knowledge Layer.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging

from engines.research.models.news_article import NewsArticle


logger = logging.getLogger(__name__)


class NewsKnowledgeEngine:
    """Управляет Knowledge Layer для новостей."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_or_find_article(
        self,
        db: Session,
        canonical_url: str,
        title: str,
        source_name: str,
        og_image_url: Optional[str] = None,
        summary: Optional[str] = None,
        author: Optional[str] = None,
        published_at = None,
        source_metadata: Optional[dict] = None,
        tags: Optional[List[str]] = None,
    ) -> tuple[NewsArticle, bool]:
        """
        Создаёт новую статью или находит существующую по URL.
        
        Returns: (article, is_new)
        """
        # Ищем существующую
        existing = db.query(NewsArticle).filter(
            NewsArticle.canonical_url == canonical_url
        ).first()
        
        if existing:
            self.logger.debug(f"Found existing article: {existing.title[:50]}")
            return existing, False
        
        # Создаём новую
        try:
            article = NewsArticle(
                canonical_url=canonical_url,
                title=title,
                source_name=source_name,
                og_image_url=og_image_url,
                summary=summary,
                author=author,
                published_at=published_at,
                source_metadata=source_metadata or {},
                tags=tags or [],
            )
            db.add(article)
            db.flush()  # Получаем ID без commit
            
            self.logger.info(f"Created new article: {title[:50]}")
            return article, True
            
        except IntegrityError:
            # Race condition — другой процесс создал одновременно
            db.rollback()
            existing = db.query(NewsArticle).filter(
                NewsArticle.canonical_url == canonical_url
            ).first()
            if existing:
                return existing, False
            raise
    
    def get_article_by_url(self, db: Session, canonical_url: str) -> Optional[NewsArticle]:
        """Получает статью по URL."""
        return db.query(NewsArticle).filter(
            NewsArticle.canonical_url == canonical_url
        ).first()
    
    def count_articles(self, db: Session, source_name: Optional[str] = None) -> int:
        """Считает количество статей."""
        query = db.query(NewsArticle)
        if source_name:
            query = query.filter(NewsArticle.source_name == source_name)
        return query.count()