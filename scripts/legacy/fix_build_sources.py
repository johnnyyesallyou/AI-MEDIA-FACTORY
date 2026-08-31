import pathlib

p = pathlib.Path("/app/engines/cross_source_enricher.py")
c = p.read_text(encoding="utf-8")

# Паттерн: если sources_data пустой, вызываем _enrich_from_source для заполнения
old_pattern = """    def _build_sources_data(self, manga_title) -> dict:
        \"\"\"
        Строит sources_data из уже обогащённого manga_title.
        Вызывается из manga_research_job для обратной совместимости.
        \"\"\"
        sources_data = {}

        # Если уже есть sources_data, возвращаем его
        if manga_title.sources_data:
            return manga_title.sources_data"""

new_pattern = """    def _build_sources_data(self, manga_title) -> dict:
        \"\"\"
        Строит sources_data из уже обогащённого manga_title.
        Вызывается из manga_research_job для обратной совместимости.
        \"\"\"
        sources_data = {}

        # Если уже есть sources_data, возвращаем его
        if manga_title.sources_data:
            return manga_title.sources_data

        # Sprint 51: если sources_data пустой, вызываем API для заполнения
        available_sources = self._get_available_sources(manga_title)
        for source in available_sources:
            try:
                self._enrich_from_source(manga_title, source)
            except Exception as e:
                self.logger.warning(f"Failed to enrich from {source}: {e}")

        if manga_title.sources_data:
            return manga_title.sources_data"""

if old_pattern in c:
    c = c.replace(old_pattern, new_pattern, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] _build_sources_data() теперь вызывает API для заполнения sources_data")
else:
    print("[!] Pattern not found")