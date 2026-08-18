"""AniList adapter - Sprint 31.

Использует AniList GraphQL API для получения anime данных.
API: https://graphql.anilist.co
Документация: https://docs.anilist.co/
"""
import logging
import requests
from core.retry import retry_external_api
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AnimeItem:
    """Единая структура для anime из любого источника."""
    external_id: str
    title: str
    title_romaji: str
    title_english: str
    title_native: str
    episodes: Optional[int]
    status: str  # RELEASING, FINISHED, NOT_YET_RELEASED, CANCELLED, HIATUS
    genres: List[str]
    cover_url: str
    source: str = "anilist"
    description: Optional[str] = None
    season: Optional[str] = None  # WINTER, SPRING, SUMMER, FALL
    season_year: Optional[int] = None


class AniListAdapter:
    """Адаптер для AniList GraphQL API."""
    
    GRAPHQL_URL = "https://graphql.anilist.co"
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @retry_external_api
    def fetch_trending_anime(self, limit: int = 20) -> List[AnimeItem]:
        """Загружает trending anime."""
        query = """
        query ($limit: Int) {
          Page(page: 1, perPage: $limit) {
            media(type: ANIME, sort: TRENDING_DESC) {
              id
              title {
                romaji
                english
                native
              }
              episodes
              status
              genres
              description(asHtml: false)
              season
              seasonYear
              coverImage {
                large
                extraLarge
              }
            }
          }
        }
        """
        
        try:
            response = requests.post(
                self.GRAPHQL_URL,
                json={"query": query, "variables": {"limit": limit}},
                headers={"Accept": "application/json"},
                timeout=15,
            )
            response.raise_for_status()
            
            data = response.json()
            media_list = data.get("data", {}).get("Page", {}).get("media", [])
            
            items = []
            for anime in media_list:
                item = self._parse_anime(anime)
                if item:
                    items.append(item)
            
            self.logger.info(f"Fetched {len(items)} trending anime from AniList")
            return items
            
        except Exception as e:
            self.logger.exception(f"AniList fetch failed: {e}")
            return []
    
    @retry_external_api
    def fetch_currently_airing(self, limit: int = 20) -> List[AnimeItem]:
        """Загружает currently airing anime."""
        query = """
        query ($limit: Int) {
          Page(page: 1, perPage: $limit) {
            media(type: ANIME, status: RELEASING, sort: POPULARITY_DESC) {
              id
              title {
                romaji
                english
                native
              }
              episodes
              status
              genres
              description(asHtml: false)
              season
              seasonYear
              coverImage {
                large
                extraLarge
              }
            }
          }
        }
        """
        
        try:
            response = requests.post(
                self.GRAPHQL_URL,
                json={"query": query, "variables": {"limit": limit}},
                headers={"Accept": "application/json"},
                timeout=15,
            )
            response.raise_for_status()
            
            data = response.json()
            media_list = data.get("data", {}).get("Page", {}).get("media", [])
            
            items = []
            for anime in media_list:
                item = self._parse_anime(anime)
                if item:
                    items.append(item)
            
            self.logger.info(f"Fetched {len(items)} currently airing anime from AniList")
            return items
            
        except Exception as e:
            self.logger.exception(f"AniList fetch failed: {e}")
            return []
    
    def _parse_anime(self, anime_data: dict) -> Optional[AnimeItem]:
        """Парсит anime данные из AniList."""
        try:
            anime_id = str(anime_data.get("id"))
            title_data = anime_data.get("title", {})
            
            title_romaji = title_data.get("romaji") or title_data.get("native") or title_data.get("english")
            title_english = title_data.get("english") or ""
            title_native = title_data.get("native") or ""
            
            if not title_romaji:
                return None
            
            cover_data = anime_data.get("coverImage", {})
            cover_url = cover_data.get("extraLarge") or cover_data.get("large") or ""
            
            # Удаляем HTML теги из description
            import re
            description = anime_data.get("description") or ""
            description = re.sub(r'<[^>]+>', '', description)
            
            return AnimeItem(
                external_id=anime_id,
                title=title_romaji,
                title_romaji=title_romaji,
                title_english=title_english,
                title_native=title_native,
                episodes=anime_data.get("episodes"),
                status=anime_data.get("status") or "UNKNOWN",
                genres=anime_data.get("genres") or [],
                cover_url=cover_url,
                source="anilist",
                description=description,
                season=anime_data.get("season"),
                season_year=anime_data.get("seasonYear"),
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse anime: {e}")
            return None
    
    @retry_external_api
    def get_anime_info(self, anime_id: str) -> Optional[AnimeItem]:
        """Получает информацию об anime по ID."""
        query = """
        query ($id: Int) {
          Media(id: $id, type: ANIME) {
            id
            title {
              romaji
              english
              native
            }
            episodes
            status
            genres
            description(asHtml: false)
            season
            seasonYear
            coverImage {
              large
              extraLarge
            }
          }
        }
        """
        
        try:
            response = requests.post(
                self.GRAPHQL_URL,
                json={"query": query, "variables": {"id": int(anime_id)}},
                headers={"Accept": "application/json"},
                timeout=15,
            )
            response.raise_for_status()
            
            data = response.json()
            anime_data = data.get("data", {}).get("Media")
            
            if not anime_data:
                return None
            
            return self._parse_anime(anime_data)
            
        except Exception as e:
            self.logger.warning(f"Failed to get anime info for {anime_id}: {e}")
            return None