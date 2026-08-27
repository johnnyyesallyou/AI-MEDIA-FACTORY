import pathlib

p = pathlib.Path("/app/backend/automation/jobs/news_publish_job.py")
c = p.read_text(encoding="utf-8")

# 1. Добавляем метод _translate_to_russian
translate_method = '''
    def _translate_to_russian(self, text: str, max_length: int = 500) -> str:
        """Sprint 52C: переводит EN текст на русский через LLM (gemma2:9b)."""
        if not text or not text.strip():
            return ""
        
        # Если уже содержит кириллицу — возвращаем как есть
        import re
        if re.search(r"[а-яА-ЯёЁ]", text):
            return text
        
        try:
            import requests
            prompt = f"""Переведи следующий текст на русский язык. Сохрани стиль и факты. Только перевод, без пояснений и комментариев.

Текст: {text[:800]}

Перевод на русском:"""
            
            response = requests.post(
                "http://host.docker.internal:11434/api/generate",
                json={
                    "model": "gemma2:9b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 600}
                },
                timeout=120,
            )
            
            if response.status_code == 200:
                translated = response.json().get("response", "").strip()
                if translated:
                    self.logger.info(f"Translated: {text[:50]}... -> {translated[:50]}...")
                    return translated[:max_length]
        except Exception as e:
            self.logger.warning(f"Translation failed: {e}")
        
        return ""  # Не возвращаем EN текст

'''

if "_translate_to_russian" not in c:
    # Вставляем перед методом _meta (строка 173)
    c = c.replace(
        '    def _meta(self, item: ContentORM) -> dict:',
        translate_method + '    def _meta(self, item: ContentORM) -> dict:',
    )
    print("[OK] Added _translate_to_russian method")
else:
    print("[i] _translate_to_russian already exists")

# 2. Применяем перевод в _build_publication
# Заменяем: title_name = news_article.title
c = c.replace(
    '''        title_name = news_article.title
        if formatting.get("unescape_html", True):
            title_name = html_lib.unescape(title_name)

        summary = news_article.summary or ""''',
    '''        title_name = news_article.title
        if formatting.get("unescape_html", True):
            title_name = html_lib.unescape(title_name)
        
        # Sprint 52C: переводим заголовок если на EN
        title_name = self._translate_to_russian(title_name, max_length=200) or title_name
        
        # Sprint 52C: переводим summary если на EN
        summary = news_article.summary or ""
        if summary:
            summary = self._translate_to_russian(summary, max_length=500) or summary''',
)

p.write_text(c, encoding="utf-8")
print("[OK] Applied translation to title + summary in _build_publication")