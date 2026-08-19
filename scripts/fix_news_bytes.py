import pathlib

p = pathlib.Path("/app/backend/automation/jobs/news_publish_job.py")
c = p.read_text(encoding="utf-8")

# Добавляем requests import
if "import requests" not in c:
    c = c.replace(
        "import html as html_lib",
        "import html as html_lib\nimport requests",
        1,
    )

# Заменяем передачу URL на скачивание + bytes upload
old = '''        # ВАЛИДАЦИЯ: проверяем что URL отдаёт реальное изображение
        if image_url and not image_resolver.is_valid_image_url(image_url):
            self.logger.warning(f"Invalid image URL (wrong content-type): {image_url[:80]}")
            image_url = None  # Сбрасываем, будем публиковать как text

        # Для news можно публиковать без картинки (как text post)
        if not image_url:
            self.logger.info(f"Publishing as text post (no valid image)")'''

new = '''        # ВАЛИДАЦИЯ: проверяем что URL отдаёт реальное изображение
        if image_url and not image_resolver.is_valid_image_url(image_url):
            self.logger.warning(f"Invalid image URL (wrong content-type): {image_url[:80]}")
            image_url = None

        # Скачиваем картинку в /tmp для news (т.к. Habr URLs без расширения ломают sendPhoto)
        image_bytes = None
        if image_url:
            try:
                headers = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
                r = requests.get(image_url, headers=headers, timeout=15)
                if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                    image_bytes = r.content
                    self.logger.debug(f"Downloaded image: {len(image_bytes)} bytes")
                else:
                    self.logger.warning(f"Image download failed: status={r.status_code}")
                    image_url = None
            except Exception as e:
                self.logger.warning(f"Image download error: {e}")
                image_url = None

        # Для news можно публиковать без картинки (как text post)
        if not image_url:
            self.logger.info(f"Publishing as text post (no valid image)")'''

if old in c:
    c = c.replace(old, new, 1)
    print("✅ Image download added")
else:
    print("❌ Marker not found (old)")

# Меняем построение Publication - сохраняем image_bytes
old2 = '''        publication = self._build_publication(
            news_article=news_article,
            item=item,
            telegraph_url=telegraph_url,
            short_url=short_url,
            image_url=image_url,
            formatting=formatting,
            publishing_policy=publishing_policy,
        )

        result = publisher.publish(publication)'''

new2 = '''        publication = self._build_publication(
            news_article=news_article,
            item=item,
            telegraph_url=telegraph_url,
            short_url=short_url,
            image_url=image_url,
            formatting=formatting,
            publishing_policy=publishing_policy,
        )
        
        # Сохраняем bytes в metadata для передачи в publisher
        if image_bytes:
            publication.metadata["_image_bytes"] = image_bytes

        result = publisher.publish(publication)'''

if old2 in c:
    c = c.replace(old2, new2, 1)
    print("✅ image_bytes passed via metadata")

p.write_text(c, encoding="utf-8")