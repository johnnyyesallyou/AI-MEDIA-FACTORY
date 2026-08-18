import pathlib

p = pathlib.Path("/app/engines/cross_source_enricher.py")
c = p.read_text(encoding="utf-8")

# Добавляем метод _build_sources_data
method = '''
    def _build_sources_data(self, manga_title) -> dict:
        """
        Строит sources_data из уже обогащённого manga_title.
        Вызывается из manga_research_job для обратной совместимости.
        """
        sources_data = {}
        
        # Если уже есть sources_data, возвращаем его
        if manga_title.sources_data:
            return manga_title.sources_data
        
        # Иначе строим из description/genres/cover
        if manga_title.description or manga_title.genres or manga_title.cover_url:
            # Определяем источник по slug
            if manga_title.title_slug:
                if self._is_readmanga_slug(manga_title.title_slug):
                    source = "readmanga"
                else:
                    source = "remanga"
                
                sources_data[source] = {
                    "description": manga_title.description,
                    "genres": manga_title.genres or [],
                    "cover_url": manga_title.cover_url,
                }
        
        return sources_data
'''

# Вставляем перед последним методом или в конец класса
if "def _build_sources_data" not in c:
    # Находим последний def в классе
    import re
    last_def = list(re.finditer(r'\n    def \w+', c))
    if last_def:
        insert_pos = last_def[-1].start()
        c = c[:insert_pos] + "\n" + method + c[insert_pos:]
        p.write_text(c, encoding="utf-8")
        print("✅ _build_sources_data added to CrossSourceEnricher")
    else:
        print("❌ Could not find insertion point")
else:
    print("ℹ️ _build_sources_data already exists")