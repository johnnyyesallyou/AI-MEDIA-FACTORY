import pathlib

p = pathlib.Path("/app/engines/publishing/image_resolver.py")
c = p.read_text(encoding="utf-8")

# Обновляем resolve() для поддержки anime_release
old = '''        if content_type == "chapter_release":
            candidates = self._manga_candidates(content)
        else:
            candidates = self._news_candidates(content, image_policy)'''

new = '''        if content_type == "chapter_release":
            candidates = self._manga_candidates(content)
        elif content_type == "anime_release":
            candidates = self._anime_candidates(content)
        else:
            candidates = self._news_candidates(content, image_policy)'''

if old in c:
    c = c.replace(old, new, 1)
    print("✅ resolve() updated for anime_release")

# Добавляем _anime_candidates метод после _manga_candidates
old2 = '''    def _news_candidates(self, content: ContentORM, image_policy: dict) -> List[Optional[str]]:'''

new2 = '''    def _anime_candidates(self, content: ContentORM) -> List[Optional[str]]:
        """AnimeEpisode -> AnimeTitle -> cover (Knowledge Layer)."""
        from core.models.anime_knowledge import AnimeTitle, AnimeEpisode
        
        candidates: List[Optional[str]] = []

        db = SessionLocal()
        try:
            if content.anime_episode_id:
                episode = db.query(AnimeEpisode).filter(
                    AnimeEpisode.id == content.anime_episode_id
                ).first()
                if episode:
                    title = db.query(AnimeTitle).filter(
                        AnimeTitle.id == episode.anime_title_id
                    ).first()
                    if title and title.cover_url:
                        candidates.append(title.cover_url)
        finally:
            db.close()

        meta = self._meta(content)
        candidates.append(meta.get("anime_cover_url"))
        candidates.append(content.image_url)
        return candidates

    def _news_candidates(self, content: ContentORM, image_policy: dict) -> List[Optional[str]]:'''

if old2 in c:
    c = c.replace(old2, new2, 1)
    print("✅ _anime_candidates() added")

p.write_text(c, encoding="utf-8")