import pathlib

p = pathlib.Path("/app/core/models/content_orm.py")
c = p.read_text(encoding="utf-8")

# Добавляем поле после anime_episode_id
marker = "    anime_episode_id = Column(String, nullable=True, index=True)"
new_field = "    anime_episode_id = Column(String, nullable=True, index=True)\n    news_article_id = Column(String, nullable=True, index=True)"

if marker in c and "news_article_id" not in c:
    c = c.replace(marker, new_field, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ news_article_id added to ContentORM")
else:
    print("ℹ️ Already exists or marker not found")