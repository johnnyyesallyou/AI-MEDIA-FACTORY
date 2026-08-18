"""Миграция: создаём таблицу news_articles"""
import sys
sys.path.insert(0, "/app")

from sqlalchemy import create_engine, text
from core.database import Base
from engines.research.models.news_article import NewsArticle
import os

print("=" * 70)
print("MIGRATION: creating news_articles table")
print("=" * 70)

engine = create_engine(os.getenv("DATABASE_URL"))

# Создаём таблицу
NewsArticle.__table__.create(engine, checkfirst=True)

print("✅ Table news_articles created")

# Проверяем
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM news_articles"))
    count = result.scalar()
    print(f"✅ Current count: {count} articles")

print("=" * 70)