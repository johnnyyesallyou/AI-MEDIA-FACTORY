import pathlib

p = pathlib.Path("/app/backend/automation/jobs/news_publish_job.py")
c = p.read_text(encoding="utf-8")

# 1. Импортируем валидацию
old = '''from engines.publishing import (
    Publication, PublicationButton,
    PublicationImageResolver, get_publisher_for_channel,
)'''

new = '''from engines.publishing import (
    Publication, PublicationButton,
    PublicationImageResolver, get_publisher_for_channel,
)'''

# 2. Добавляем валидацию в _publish_one перед построением Publication
old2 = '''        # Image через Publishing Layer (policy-driven)
        image_url = image_resolver.resolve(item, channel)
        if not image_url:
            # Fallback: og_image из NewsArticle
            image_url = news_article.og_image_url

        # Для news можно опубликовать без картинки (текст)
        # Но если image_policy.fallback != 'none' — попробуем
        if not image_url:
            image_policy = profile.get("image_policy", {})
            if image_policy.get("fallback") == "none":
                return {"status": "failed", "error": "No image resolved"}
            # Иначе публикуем без картинки (будет text post)'''

new2 = '''        # Image через Publishing Layer (с ВАЛИДАЦИЕЙ)
        image_url = image_resolver.resolve(item, channel)
        if not image_url:
            # Fallback: og_image из NewsArticle
            image_url = news_article.og_image_url
        
        # ВАЛИДАЦИЯ: проверяем что URL отдаёт реальное изображение
        if image_url and not image_resolver.is_valid_image_url(image_url):
            self.logger.warning(f"Invalid image URL (wrong content-type): {image_url[:80]}")
            image_url = None  # Сбрасываем, будем публиковать как text
        
        # Для news можно публиковать без картинки (как text post)
        if not image_url:
            self.logger.info(f"Publishing as text post (no valid image)")'''

if old2 in c:
    c = c.replace(old2, new2, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ NewsPublishJob: image validation added")
else:
    print("❌ Marker not found")