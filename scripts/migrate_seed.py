import sys, json
sys.path.insert(0, "/app")
from sqlalchemy import text
from core.database import SessionLocal, engine
from core.models.channel_orm import ChannelORM
from engines.channel_profiles import guess_profile_key, resolve_channel_profile

# 1. Миграция: добавляем колонку
table = ChannelORM.__tablename__
with engine.connect() as conn:
    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS content_profile JSONB"))
    conn.commit()
print(f"✅ Migration: {table}.content_profile JSONB added")

# 2. Seed: привязываем профиль к каждому каналу
db = SessionLocal()
for ch in db.query(ChannelORM).all():
    key = guess_profile_key(ch)
    ch.content_profile = {"profile_key": key}
    print(f"  {ch.name} -> {key}")
db.commit()

# 3. Проверка: резолвим полные профили
print("\nResolved profiles:")
for ch in db.query(ChannelORM).all():
    p = resolve_channel_profile(ch)
    print(f"\n  [{ch.name}]")
    print(f"    theme={p['theme']} type={p['content_type']} lang={p['language']}")
    print(f"    sources={p['sources']}")
    print(f"    image: mode={p['image_policy']['mode']} preferred={p['image_policy']['preferred']} fallback={p['image_policy']['fallback']}")
    print(f"    publish: ru_title={p['publishing_policy']['require_ru_title']} telegraph={p['publishing_policy']['telegraph_page']} buttons={p['publishing_policy']['inline_buttons']}")
    print(f"    format: emoji={p['formatting_profile']['emoji_header']} hashtags<={p['formatting_profile']['max_hashtags']}")
db.close()
print("\n✅ Sprint 20 config layer ready")