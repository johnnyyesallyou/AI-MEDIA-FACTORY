"""Anime Research Job - Sprint 31.

Использует AnimeKnowledgeEngine как единый источник истины:
1. Fetch anime через AnimeRegistry
2. Передать в AnimeKnowledgeEngine (создаёт AnimeTitle + AnimeEpisode)
3. Только НОВЫЕ AnimeEpisode → ContentORM со ссылкой на anime_episode_id
4. Повторный запуск не создаёт дубликатов
"""
import logging
from typing import Any, Dict
from datetime import datetime
import uuid
import json

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from core.models.anime_knowledge import AnimeTitle, AnimeEpisode
from engines.source_adapters.anime_registry import AnimeRegistry
from engines.anime_knowledge_engine import AnimeKnowledgeEngine

logger = logging.getLogger(__name__)


class AnimeResearchJob:
    """Orchestrates anime research via Knowledge Layer."""

    ANIME_CHANNEL_ID = "anime-channel-001"

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.knowledge = AnimeKnowledgeEngine()

    def run(self, channel: ChannelORM = None, limit_per_source: int = 20) -> Dict[str, Any]:
        self.logger.info(f"AnimeResearchJob started (limit_per_source={limit_per_source})")

        db = SessionLocal()

        try:
            anime_channel = channel or self._get_anime_channel(db)
            if not anime_channel:
                self.logger.error("Anime channel not found!")
                return {"status": "failed", "error": "Anime channel not found"}

            sources = AnimeRegistry.available_sources()

            if not sources:
                self.logger.warning("No valid sources")
                return {"status": "ok", "new_episodes": 0, "sources": sources}

            self.logger.info(f"Fetching from sources: {sources}")

            # 1. Fetch anime через AnimeRegistry (trending + airing)
            all_items = []
            for source in sources:
                trending = AnimeRegistry.fetch_trending(limit=limit_per_source // 2, source=source)
                airing = AnimeRegistry.fetch_currently_airing(limit=limit_per_source // 2, source=source)
                all_items.extend(trending)
                all_items.extend(airing)

            if not all_items:
                self.logger.warning("No items fetched")
                return {"status": "ok", "new_episodes": 0, "sources": sources}

            self.logger.info(f"Fetched {len(all_items)} items from {len(sources)} sources")

            # 2. Передаём в Knowledge Layer (в ТОЙ ЖЕ сессии)
            result = self.knowledge.process_items(db, all_items)

            self.logger.info(
                f"Knowledge Layer: {result.new_titles} new titles, "
                f"{result.new_episodes} new episodes, "
                f"{result.existing_episodes} existing"
            )

            if not result.new_episode_ids:
                return {
                    "status": "ok",
                    "new_episodes": 0,
                    "existing": result.existing_episodes,
                    "sources": sources,
                }

            # 3. Загружаем AnimeEpisode объекты из текущей сессии
            new_episodes = db.query(AnimeEpisode).filter(
                AnimeEpisode.id.in_(result.new_episode_ids)
            ).all()

            self.logger.info(f"Creating {len(new_episodes)} ContentORM items...")
            research_items_created = 0

            for episode in new_episodes:
                try:
                    title = db.query(AnimeTitle).filter(
                        AnimeTitle.id == episode.anime_title_id
                    ).first()
                    if not title:
                        continue

                    research_item = self._create_research_item(
                        db=db,
                        episode=episode,
                        title=title,
                        channel=anime_channel,
                    )
                    if research_item:
                        research_items_created += 1
                except Exception as e:
                    self.logger.error(f"Failed to create research item: {e}")

            db.commit()

            final_result = {
                "status": "ok",
                "new_episodes": research_items_created,
                "existing": result.existing_episodes,
                "new_titles": result.new_titles,
                "sources": sources,
            }

            self.logger.info(f"AnimeResearchJob completed: {final_result}")
            return final_result

        except Exception as e:
            db.rollback()
            self.logger.exception(f"AnimeResearchJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()

    def _get_anime_channel(self, db) -> ChannelORM:
        channel = db.query(ChannelORM).filter(
            ChannelORM.id == self.ANIME_CHANNEL_ID
        ).first()
        if not channel:
            channel = db.query(ChannelORM).filter(
                ChannelORM.name.like("%Аниме%") | ChannelORM.name.like("%Anime%")
            ).first()
        return channel

    def _create_research_item(
        self,
        db: SessionLocal,
        episode: AnimeEpisode,
        title: AnimeTitle,
        channel: ChannelORM,
    ) -> ContentORM:
        """Создаёт ContentORM со ссылкой на AnimeEpisode."""
        title_name = title.canonical_title
        if title.aliases and "romaji" in title.aliases:
            title_name = title.aliases["romaji"]

        headline = f"🎬 Новое аниме: {title_name}"
        if title.season and title.season_year:
            headline += f" ({title.season} {title.season_year})"

        metadata = {
            "type": "anime_release",
            "anime_source": episode.source,
            "anime_title_id": title.id,
            "anime_title_canonical": title.canonical_title,
            "anime_title_romaji": title.title_romaji,
            "anime_title_english": title.title_english,
            "anime_title_native": title.title_native,
            "anime_title_aliases": title.aliases or {},
            "anime_title_external_ids": title.external_ids or {},
            "anime_episode_number": episode.episode_number,
            "anime_episode_id": episode.id,
            "anime_episode_external_id": episode.external_id,
            "anime_cover_url": title.cover_url,
            "anime_description": title.description,
            "anime_genres": title.genres,
            "anime_status": title.status,
            "anime_season": title.season,
            "anime_season_year": title.season_year,
            "anime_episodes_total": title.episodes,
        }

        research_item = ContentORM(
            id=str(uuid.uuid4()),
            channel_id=channel.id,
            headline=headline,
            draft_text=headline,
            source_url="",  # AniList не даёт прямых URL
            source_text=json.dumps(metadata, ensure_ascii=False),
            anime_episode_id=episode.id,
            status="research",
            created_at=datetime.utcnow(),
        )
        db.add(research_item)
        self.logger.debug(f"Created research item: {headline[:50]} (episode_id={episode.id[:8]})")
        return research_item