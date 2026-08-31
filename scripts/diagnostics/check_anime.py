import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.anime_knowledge import AnimeTitle, AnimeEpisode

db = SessionLocal()
titles = db.query(AnimeTitle).count()
episodes = db.query(AnimeEpisode).count()
print(f"Anime titles: {titles}")
print(f"Anime episodes: {episodes}")

# Проверяем статус эпизодов
from core.models.content_orm import ContentORM
research_items = db.query(ContentORM).filter(ContentORM.status == "research").count()
published_items = db.query(ContentORM).filter(ContentORM.status == "published").count()
print(f"ContentORM: research={research_items}, published={published_items}")
db.close()