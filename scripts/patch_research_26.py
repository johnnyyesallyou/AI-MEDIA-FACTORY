import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_research_job.py")
c = p.read_text(encoding="utf-8")

# Добавляем импорт CrossSourceEnricher
if "from engines.cross_source_enricher" not in c:
    c = c.replace(
        "from engines.manga_knowledge_engine import MangaKnowledgeEngine",
        "from engines.manga_knowledge_engine import MangaKnowledgeEngine\nfrom engines.cross_source_enricher import CrossSourceEnricher",
        1
    )

# Добавляем self.enricher в __init__
if "self.enricher" not in c:
    c = c.replace(
        "self.knowledge = MangaKnowledgeEngine()",
        "self.knowledge = MangaKnowledgeEngine()\n        self.enricher = CrossSourceEnricher()",
        1
    )

# Добавляем enrichment после process_items
old_section = '''            self.logger.info(
                f"Knowledge Layer: {result.new_titles} new titles, "
                f"{result.new_chapters} new chapters, "
                f"{result.existing_chapters} existing"
            )

            if not result.new_chapter_ids:'''

new_section = '''            self.logger.info(
                f"Knowledge Layer: {result.new_titles} new titles, "
                f"{result.new_chapters} new chapters, "
                f"{result.existing_chapters} existing"
            )

            # Sprint 26: Enrichment для новых тайтлов
            if result.new_chapter_ids:
                try:
                    self._enrich_new_titles(db, result.new_chapter_ids)
                except Exception as e:
                    self.logger.warning(f"Enrichment failed: {e}")

            if not result.new_chapter_ids:'''

if old_section in c and "self._enrich_new_titles" not in c:
    c = c.replace(old_section, new_section, 1)
    
    # Добавляем метод _enrich_new_titles
    enrich_method = '''

    def _enrich_new_titles(self, db, chapter_ids):
        """Обогащает тайтлы, связанные с новыми главами."""
        from core.models.manga_knowledge import MangaChapter, MangaTitle
        
        # Находим уникальные manga_title_id
        chapters = db.query(MangaChapter).filter(
            MangaChapter.id.in_(chapter_ids)
        ).all()
        title_ids = list(set(ch.manga_title_id for ch in chapters))
        
        # Загружаем тайтлы без описания
        titles = db.query(MangaTitle).filter(
            MangaTitle.id.in_(title_ids),
            (MangaTitle.description == None) | (MangaTitle.description == "")
        ).all()
        
        enriched = 0
        for title in titles:
            try:
                sources_data = self.enricher.fetch_source_data(title)
                if sources_data != (title.sources_data or {}):
                    title.sources_data = sources_data
                
                desc, genres, cover = self.enricher.merge(sources_data)
                
                if desc and not title.description:
                    title.description = desc
                if genres and not title.genres:
                    title.genres = genres
                if cover and not title.cover_url:
                    title.cover_url = cover
                
                if desc or genres:
                    enriched += 1
                    self.logger.info(f"Enriched: {title.canonical_title[:40]}")
            except Exception as e:
                self.logger.warning(f"Enrichment failed for {title.canonical_title[:40]}: {e}")
        
        if enriched:
            self.logger.info(f"Enriched {enriched} new titles")
'''
    
    # Вставляем метод перед _get_manga_channel
    marker = "    def _get_manga_channel(self, db)"
    if marker in c:
        c = c.replace(marker, enrich_method + "\n" + marker, 1)
    
    p.write_text(c, encoding="utf-8")
    print("✅ MangaResearchJob: auto-enrichment added")
else:
    print("ℹ️ Already patched")