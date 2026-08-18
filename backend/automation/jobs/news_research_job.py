"""News Research Job - Sprint 32.

Загружает новости из RSS, создаёт NewsArticle в Knowledge Layer.
Дедупликация по URL.

Pipeline:
  RSSSource (habr/vc/etc) → Article
       ↓
  NewsKnowledgeEngine (dedup by canonical_url)
       ↓
  NewsArticle (создан или найден)
       ↓
  SourceImageResolver (og:image → cover_image_url)
       ↓
  ContentORM (с news_article_id, status=research)
"""
import logging
from typing import Any, Dict, List
from datetime import datetime
import uuid
import json
import re

from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.research.models.news_article import NewsArticle
from engines.news_knowledge_engine import NewsKnowledgeEngine
from engines.source_image_resolver import SourceImageResolver
from engines.research.sources.rss import RSSSource

logger = logging.getLogger(__name__)


# Конфигурация RSS источников
RSS_FEEDS = [
    {
        "name": "habr",
        "url": "https://habr.com/ru/rss/articles/",
        "language": "ru",
        "trust_score": 80,
        "categories": ["tech", "ai", "programming"],
    },
    {
        "name": "vc",
        "url": "https://vc.ru/rss/all",
        "language": "ru",
        "trust_score": 70,
        "categories": ["business", "tech", "startups"],
    },
    {
        "name": "techcrunch",
        "url": "https://techcrunch.com/feed/",
        "language": "en",
        "trust_score": 90,
        "categories": ["tech", "ai", "startups"],
    },
    {
        "name": "theverge",
        "url": "https://www.theverge.com/rss/index.xml",
        "language": "en",
        "trust_score": 85,
        "categories": ["tech", "ai", "gadgets"],
    },
]


class NewsResearchJob:
    """Orchestrates news research via Knowledge Layer."""

    NEWS_CHANNEL_ID = "news-channel-001"

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.knowledge = NewsKnowledgeEngine()
        self.image_resolver = SourceImageResolver()

    def run(
        self,
        channel: ChannelORM = None,
        limit_per_source: int = 10,
        sources: List[str] = None,
    ) -> Dict[str, Any]:
        self.logger.info(f"NewsResearchJob started (limit_per_source={limit_per_source})")

        db = SessionLocal()
        try:
            news_channel = channel or self._get_news_channel(db)
            if not news_channel:
                self.logger.error("News channel not found!")
                return {"status": "failed", "error": "News channel not found"}

            # Какие источники используем
            feeds = RSS_FEEDS
            if sources:
                feeds = [f for f in feeds if f["name"] in sources]

            if not feeds:
                self.logger.warning("No RSS feeds configured")
                return {"status": "ok", "new_articles": 0, "sources": []}

            all_articles = []
            source_counts = {}

            # 1. Fetch from each source
            for feed_config in feeds:
                try:
                    source = RSSSource(feed_config)
                    articles = source.fetch(max_items=limit_per_source)
                    source_counts[feed_config["name"]] = len(articles)
                    all_articles.extend([(feed_config["name"], a) for a in articles])
                    self.logger.info(f"Fetched {len(articles)} from {feed_config['name']}")
                except Exception as e:
                    self.logger.warning(f"Failed to fetch from {feed_config['name']}: {e}")
                    source_counts[feed_config["name"]] = 0

            if not all_articles:
                return {"status": "ok", "new_articles": 0, "sources": list(source_counts.keys())}

            self.logger.info(f"Total fetched: {len(all_articles)}")

            # 2. Process через Knowledge Layer (dedup по URL)
            new_articles_count = 0
            new_article_ids: List[str] = []
            image_extracted = 0

            for source_name, article in all_articles:
                try:
                    canonical_url = self._normalize_url(article.url)
                    if not canonical_url:
                        continue

                    # Извлекаем og:image из HTML
                    og_image = None
                    try:
                        og_image = self._extract_og_image(article.url)
                        if og_image:
                            image_extracted += 1
                    except Exception as e:
                        self.logger.debug(f"og:image extraction failed: {e}")

                    # Создаём/находим NewsArticle
                    news_article, is_new = self.knowledge.create_or_find_article(
                        db=db,
                        canonical_url=canonical_url,
                        title=article.title,
                        source_name=source_name,
                        og_image_url=og_image,
                        summary=article.summary if hasattr(article, 'summary') else None,
                        author=article.author if hasattr(article, 'author') else None,
                        published_at=article.published_at if hasattr(article, 'published_at') else None,
                        source_metadata={
                            "rss_link": article.url,
                            "categories": feed_config.get("categories", []),
                            "language": feed_config.get("language", "en"),
                        },
                        tags=article.tags if hasattr(article, 'tags') else [],
                    )

                    if is_new:
                        new_articles_count += 1
                        new_article_ids.append(str(news_article.id))

                except Exception as e:
                    self.logger.warning(f"Failed to process article: {e}")

            # 3. Создаём ContentORM только для НОВЫХ статей
            self.logger.info(f"Creating {len(new_article_ids)} ContentORM items...")
            research_items_created = 0

            for article_id in new_article_ids:
                try:
                    article = db.query(NewsArticle).filter(
                        NewsArticle.id == article_id
                    ).first()
                    if not article:
                        continue

                    research_item = self._create_research_item(
                        db=db,
                        article=article,
                        channel=news_channel,
                    )
                    if research_item:
                        research_items_created += 1
                except Exception as e:
                    self.logger.error(f"Failed to create research item: {e}")

            db.commit()

            result = {
                "status": "ok",
                "fetched_total": len(all_articles),
                "new_articles": research_items_created,
                "existing_articles": len(all_articles) - new_articles_count,
                "images_extracted": image_extracted,
                "sources": source_counts,
            }

            self.logger.info(f"NewsResearchJob completed: {result}")
            return result

        except Exception as e:
            db.rollback()
            self.logger.exception(f"NewsResearchJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()

    def _get_news_channel(self, db) -> ChannelORM:
        """Находит news канал."""
        channel = db.query(ChannelORM).filter(
            ChannelORM.name.like("%Новост%") | ChannelORM.name.like("%News%")
        ).first()
        return channel

    def _normalize_url(self, url: str) -> str:
        """Нормализует URL для дедупликации."""
        if not url:
            return ""
        # Убираем tracking параметры
        url = re.sub(r'\?utm_[^&]+(&|$)', '', url)
        url = re.sub(r'&utm_[^&]+', '', url)
        url = url.rstrip('?&')
        return url

    def _extract_og_image(self, url: str) -> str:
        """Быстро извлекает og:image из HTML."""
        import requests
        from bs4 import BeautifulSoup

        try:
            r = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"
            }, timeout=10)
            if r.status_code != 200:
                return None

            soup = BeautifulSoup(r.text, "html.parser")

            # og:image
            og = soup.find("meta", attrs={"property": "og:image"})
            if og and og.get("content"):
                return og["content"]

            # twitter:image
            tw = soup.find("meta", attrs={"name": "twitter:image"})
            if tw and tw.get("content"):
                return tw["content"]

            return None
        except Exception:
            return None

    def _create_research_item(
        self,
        db: Session,
        article: NewsArticle,
        channel: ChannelORM,
    ) -> ContentORM:
        """Создаёт ContentORM со ссылкой на NewsArticle."""
        headline = f"📰 {article.title}"

        metadata = {
            "type": "news",
            "news_article_id": str(article.id),
            "news_source": article.source_name,
            "news_canonical_url": article.canonical_url,
            "news_author": article.author,
            "news_og_image": article.og_image_url,
            "news_summary": article.summary,
            "news_tags": article.tags,
            "news_published_at": article.published_at.isoformat() if article.published_at else None,
        }

        research_item = ContentORM(
            id=str(uuid.uuid4()),
            channel_id=channel.id,
            headline=headline,
            draft_text=article.summary or article.title,
            source_url=article.canonical_url,
            source_text=json.dumps(metadata, ensure_ascii=False),
            news_article_id=str(article.id),
            image_url=article.og_image_url,
            status="research",
            created_at=datetime.utcnow(),
        )
        db.add(research_item)
        self.logger.debug(f"Created research item: {headline[:50]}")
        return research_item