import pathlib

p = pathlib.Path("/app/backend/automation/jobs/anime_research_job.py")
c = p.read_text(encoding="utf-8")

# Находим создание ContentORM и добавляем anime_episode_id
old = '''        research_item = ContentORM(
            id=str(uuid.uuid4()),
            channel_id=channel.id,
            headline=headline,
            draft_text=headline,
            source_url="",  # AniList не даёт прямых URL
            source_text=json.dumps(metadata, ensure_ascii=False),
            status="research",
            created_at=datetime.utcnow(),
        )'''

new = '''        research_item = ContentORM(
            id=str(uuid.uuid4()),
            channel_id=channel.id,
            headline=headline,
            draft_text=headline,
            source_url="",  # AniList не даёт прямых URL
            source_text=json.dumps(metadata, ensure_ascii=False),
            anime_episode_id=episode.id,
            status="research",
            created_at=datetime.utcnow(),
        )'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ anime_episode_id added to ContentORM creation")
else:
    print("❌ Marker not found")