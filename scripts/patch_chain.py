import pathlib

p = pathlib.Path("/app/engines/publishing/image_acquisition.py")
c = p.read_text(encoding="utf-8")

# 1. Lazy properties для новых адаптеров
old = '''    @property
    def validator(self):'''
new = '''    @property
    def unsplash(self):
        """Lazy init UnsplashAdapter."""
        if not hasattr(self, "_unsplash"):
            from engines.image.unsplash_adapter import UnsplashAdapter
            self._unsplash = UnsplashAdapter()
        return self._unsplash

    @property
    def dalle(self):
        """Lazy init DALLEAdapter."""
        if not hasattr(self, "_dalle"):
            from engines.image.dalle_adapter import DALLEAdapter
            self._dalle = DALLEAdapter()
        return self._dalle

    @property
    def validator(self):'''

if old in c:
    c = c.replace(old, new, 1)
    print("✅ Lazy properties added")

# 2. Переключаем acquire на fallback chain
old2 = '''        # 2. AI fallback — ТОЛЬКО для news и ТОЛЬКО если разрешено профилем
        if content_type == "news" and fallback == "ai_generated":
            return self._ai_fallback(content, image_policy)'''

new2 = '''        # 2. Fallback chain — ТОЛЬКО для news и ТОЛЬКО если разрешено профилем
        if content_type == "news" and fallback == "ai_generated":
            return self._fallback_chain(content, image_policy)'''

if old2 in c:
    c = c.replace(old2, new2, 1)
    print("✅ acquire() uses fallback chain")

# 3. Добавляем _fallback_chain перед _ai_fallback
old3 = '''    def _ai_fallback(self, content, image_policy: dict) -> AcquisitionResult:'''

new3 = '''    def _fallback_chain(self, content, image_policy: dict) -> AcquisitionResult:
        """
        Fallback chain для news (Sprint 38):
          1. Unsplash (stock photo по ключевым словам)
          2. DALL-E (AI генерация, если есть OPENAI_API_KEY)
          3. Pollinations (бесплатный AI, без ключа)

        Источники без API ключей gracefully пропускаются.
        """
        chain = image_policy.get("fallback_chain", ["unsplash", "dalle", "pollinations"])
        query = (content.headline or "").replace("📰", "").strip()[:80]

        for source in chain:
            try:
                if source == "unsplash" and self.unsplash.available:
                    url = self.unsplash.get_best_image(query)
                    if url:
                        return AcquisitionResult(url=url, source="unsplash")

                elif source == "dalle" and self.dalle.available:
                    url = self.dalle.generate(f"News illustration: {query}")
                    if url:
                        return AcquisitionResult(url=url, source="dalle")

                elif source == "pollinations":
                    return self._ai_fallback(content, image_policy)

            except Exception as e:
                self.logger.warning(f"Fallback source {source} failed: {e}")

        return AcquisitionResult(url=None, source="none")

    def _ai_fallback(self, content, image_policy: dict) -> AcquisitionResult:'''

if old3 in c:
    c = c.replace(old3, new3, 1)
    print("✅ _fallback_chain added")

p.write_text(c, encoding="utf-8")