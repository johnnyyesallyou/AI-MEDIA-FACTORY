"""Anime Knowledge Engine - Sprint 31.

Связывает AnimeItem с уникальными AnimeTitle сущностями.
Аналог MangaKnowledgeEngine для anime.
"""
import logging
import uuid
from typing import Optional, List, Tuple, Set, NamedTuple
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from core.models.anime_knowledge import AnimeTitle, AnimeEpisode
from engines.source_adapters.anilist_adapter import AnimeItem
from engines.title_normalizer import TitleNormalizer

logger = logging.getLogger(__name__)


class AnimeProcessingResult(NamedTuple):
    """Результат обработки AnimeItems."""
    new_titles: int
    new_episodes: int
    existing_episodes: int
    skipped_duplicates: int
    new_episode_ids: List[str]


class AnimeKnowledgeEngine:
    """
    Связывает AnimeItem с базой знаний об anime.
    
    НЕ создаёт свою сессию — работает с переданной извне.
    НЕ делает commit/rollback — это ответственность вызывающего кода.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.normalizer = TitleNormalizer()

    def process_items(self, db, items: List[AnimeItem]) -> AnimeProcessingResult:
        """
        Обрабатывает список AnimeItems в переданной сессии.
        
        Returns:
            AnimeProcessingResult со списком ID новых AnimeEpisode
        """
        new_titles_count = 0
        new_episodes = 0
        existing_episodes = 0
        skipped_duplicates = 0
        new_episode_ids: List[str] = []

        seen_episodes: Set[Tuple[str, str, str, str]] = set()
        titles_cache: dict = {}

        for item in items:
            # 1. Находим/создаём тайтл
            title, title_is_new = self._find_or_create_title(db, item, titles_cache)
            if title is None:
                continue

            if title_is_new:
                new_titles_count += 1

            # 2. In-memory дедупликация
            title_id = title.id
            # Для anime: episode_number (пока используем "1" как placeholder)
            episode_key = (title_id, "1", "1", item.source)  # (title_id, ep_num, season, source)
            if episode_key in seen_episodes:
                skipped_duplicates += 1
                continue

            # 3. Находим/создаём эпизод
            episode_id, created = self._find_or_create_episode(db, title_id, item)

            if created:
                new_episodes += 1
                seen_episodes.add(episode_key)
                new_episode_ids.append(episode_id)
            else:
                existing_episodes += 1

        self.logger.info(
            f"Processed: {len(items)} items -> "
            f"{new_titles_count} new titles, {new_episodes} new episodes, "
            f"{existing_episodes} existing, {skipped_duplicates} batch duplicates"
        )

        return AnimeProcessingResult(
            new_titles=new_titles_count,
            new_episodes=new_episodes,
            existing_episodes=existing_episodes,
            skipped_duplicates=skipped_duplicates,
            new_episode_ids=new_episode_ids,
        )

    def _find_or_create_title(
        self,
        db,
        item: AnimeItem,
        cache: dict,
    ) -> Tuple[Optional[AnimeTitle], bool]:
        normalized = self.normalizer.normalize(item.title)
        if not normalized:
            return None, False

        if normalized in cache:
            title = cache[normalized]
            self._update_external_ids(title, item)
            return title, False

        title = db.query(AnimeTitle).filter(
            AnimeTitle.canonical_title == normalized
        ).first()

        if title:
            self._update_external_ids(title, item)
            cache[normalized] = title
            return title, False

        title = AnimeTitle(
            id=str(uuid.uuid4()),
            canonical_title=normalized,
            title_romaji=item.title_romaji,
            title_english=item.title_english,
            title_native=item.title_native,
            title_slug=None,  # AniList не использует slug
            aliases=self._build_aliases(item),
            external_ids={item.source: item.external_id} if item.external_id else {},
            sources_data={item.source: {
                "description": item.description,
                "genres": item.genres,
                "cover_url": item.cover_url,
                "status": item.status,
                "episodes": item.episodes,
                "season": item.season,
                "season_year": item.season_year,
            }},
            description=item.description,
            genres=item.genres,
            cover_url=item.cover_url,
            status=item.status,
            season=item.season,
            season_year=item.season_year,
            episodes=item.episodes,
        )
        db.add(title)
        db.flush()

        cache[normalized] = title
        return title, True

    def _find_or_create_episode(
        self,
        db,
        title_id: str,
        item: AnimeItem,
    ) -> Tuple[str, bool]:
        """Возвращает (episode_id, is_new)."""
        # Для anime пока используем episode "1" как placeholder
        # В будущем можно парсить конкретные эпизоды
        episode_number = "1"
        season_number = 1

        existing = db.query(AnimeEpisode).filter(
            AnimeEpisode.anime_title_id == title_id,
            AnimeEpisode.episode_number == episode_number,
            AnimeEpisode.season_number == season_number,
            AnimeEpisode.source == item.source,
        ).first()

        if existing:
            return existing.id, False

        episode_id = str(uuid.uuid4())
        episode = AnimeEpisode(
            id=episode_id,
            anime_title_id=title_id,
            episode_number=episode_number,
            season_number=season_number,
            source=item.source,
            external_id=item.external_id,
            language="ja",
            title=item.title,
            description=item.description,
            aired_at=None,
        )
        db.add(episode)

        try:
            db.flush()
            return episode_id, True
        except IntegrityError:
            db.rollback()
            existing = db.query(AnimeEpisode).filter(
                AnimeEpisode.anime_title_id == title_id,
                AnimeEpisode.episode_number == episode_number,
                AnimeEpisode.season_number == season_number,
                AnimeEpisode.source == item.source,
            ).first()
            if existing:
                return existing.id, False
            raise

    def _update_external_ids(self, title: AnimeTitle, item: AnimeItem):
        if not item.external_id:
            return
        external_ids = dict(title.external_ids or {})
        if item.source not in external_ids:
            external_ids[item.source] = item.external_id
            title.external_ids = external_ids

    def _build_aliases(self, item: AnimeItem) -> dict:
        aliases = {}
        if item.title_romaji:
            aliases["romaji"] = item.title_romaji
        if item.title_english:
            aliases["en"] = item.title_english
        if item.title_native:
            aliases["ja"] = item.title_native
        return aliases