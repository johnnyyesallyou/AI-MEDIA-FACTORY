import pathlib

p = pathlib.Path("/app/backend/automation/jobs/anime_publish_job.py")
c = p.read_text(encoding="utf-8")

# Добавляем метод для перевода описания через LLM
translate_method = '''
    def _translate_to_russian(self, text: str, max_length: int = 500) -> str:
        """Sprint 51: переводит EN описание на русский через LLM (gemma2:9b)."""
        if not text or not text.strip():
            return ""
        
        # Если уже содержит кириллицу — возвращаем как есть
        import re
        if re.search(r"[а-яА-ЯёЁ]", text):
            return text
        
        try:
            import requests
            prompt = f"""Переведи описание аниме на русский язык. Сохрани стиль и эмоции. Только перевод, без пояснений.

Описание: {text[:800]}

Перевод на русском:"""
            
            response = requests.post(
                "http://host.docker.internal:11434/api/generate",
                json={
                    "model": "gemma2:9b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3}
                },
                timeout=60,
            )
            
            if response.status_code == 200:
                translated = response.json().get("response", "").strip()
                if translated:
                    return translated[:max_length]
        except Exception as e:
            self.logger.warning(f"Translation failed: {e}")
        
        return ""  # Не возвращаем EN текст, пусть будет пустой
    
'''

# Вставляем перед методом _build_caption или в начало класса
if "_translate_to_russian" not in c:
    c = c.replace(
        'class AnimePublishJob:',
        'class AnimePublishJob:' + translate_method,
    )
    
    # Используем перевод в _build_caption
    c = c.replace(
        '        description = anime_title.description or ""\n        if publishing_policy.get("strip_non_ru_description") and not re.search(r"[а-яА-ЯёЁ]", description):\n            description = ""',
        '        description = anime_title.description or ""\n        # Sprint 51: переводим EN описание на русский\n        if publishing_policy.get("strip_non_ru_description") and not re.search(r"[а-яА-ЯёЁ]", description):\n            translated = self._translate_to_russian(description)\n            description = translated  # если перевод не удался — будет пусто',
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] FIX 5: AnimePublishJob — добавлен LLM перевод описания")
else:
    print("[i] _translate_to_russian already exists")