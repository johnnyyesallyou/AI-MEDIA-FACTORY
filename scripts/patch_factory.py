import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

# Импорт factory
old_imp = """from engines.publishing import (
    Publication, PublicationButton,
    TelegramPlatformPublisher, PublicationImageResolver,
)"""
new_imp = """from engines.publishing import (
    Publication, PublicationButton,
    PublicationImageResolver, get_publisher_for_channel,
)"""
if old_imp in c:
    c = c.replace(old_imp, new_imp, 1)

# Замена создания publisher
old_pub = "publisher = TelegramPlatformPublisher(manga_channel.bot_token, manga_channel.chat_id)"
new_pub = "publisher = get_publisher_for_channel(manga_channel)"
if old_pub in c:
    c = c.replace(old_pub, new_pub, 1)

p.write_text(c, encoding="utf-8")
print("✅ MangaPublishJob uses get_publisher_for_channel")