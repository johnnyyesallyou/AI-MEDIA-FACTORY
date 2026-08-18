import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.knowledge_source_orm import KnowledgeSourceORM
from datetime import datetime

db = SessionLocal()
try:
    # Находим канал AI Anime News
    from core.models.channel_orm import ChannelORM
    anime_channel = db.query(ChannelORM).filter(ChannelORM.name.like('%Anime%')).first()
    
    if not anime_channel:
        print('Канал AI Anime News не найден')
        sys.exit(1)
    
    print(f'Канал: {anime_channel.name} (id={anime_channel.id})')
    
    # Удаляем все старые источники
    old_sources = db.query(KnowledgeSourceORM).filter(
        KnowledgeSourceORM.channel_id == anime_channel.id
    ).all()
    
    print(f'Удаляем {len(old_sources)} старых источников...')
    for src in old_sources:
        db.delete(src)
    
    # Добавляем правильные аниме источники
    anime_sources = [
        {
            'name': 'Anime News Network',
            'source_type': 'rss',
            'url': 'https://www.animenewsnetwork.com/all/rss.xml',
            'is_active': True,
            'priority': 1
        },
        {
            'name': 'Crunchyroll News',
            'source_type': 'rss',
            'url': 'https://www.crunchyroll.com/news/rss',
            'is_active': True,
            'priority': 2
        },
        {
            'name': 'MyAnimeList News',
            'source_type': 'rss',
            'url': 'https://myanimelist.net/rss/news.xml',
            'is_active': True,
            'priority': 3
        },
        {
            'name': 'Google News Anime',
            'source_type': 'rss',
            'url': 'https://news.google.com/rss/search?q=anime+series+manga&hl=en&gl=US&ceid=US:en',
            'is_active': True,
            'priority': 4
        },
        {
            'name': 'Reddit r/anime',
            'source_type': 'rss',
            'url': 'https://www.reddit.com/r/anime/.rss',
            'is_active': True,
            'priority': 5
        }
    ]
    
    for src_data in anime_sources:
        source = KnowledgeSourceORM(
            channel_id=anime_channel.id,
            name=src_data['name'],
            source_type=src_data['source_type'],
            url=src_data['url'],
            is_active=src_data['is_active'],
            priority=src_data['priority'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(source)
        print(f'  + {src_data["name"]}')
    
    db.commit()
    print(f'\\n✅ Источники обновлены: {len(anime_sources)} аниме источников')
finally:
    db.close()