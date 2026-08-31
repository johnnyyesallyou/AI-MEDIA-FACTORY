import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from datetime import datetime

db = SessionLocal()
try:
    # Находим канал AI Anime News
    anime_channel = db.query(ChannelORM).filter(ChannelORM.name.like('%Anime%')).first()
    
    if not anime_channel:
        print('❌ Канал AI Anime News не найден')
        sys.exit(1)
    
    print(f'Канал: {anime_channel.name} (id={anime_channel.id})')
    
    # Создаём тестовый approved пост БЕЗ image_url
    post = ContentORM(
        channel_id=anime_channel.id,
        source_url='https://test.com/jujutsu-kaisen-season-3',
        headline='«Магическая битва»: анонсирован 3 сезон',
        source_text='Studio MAPPA анонсировала третий сезон популярного аниме Магическая битва',
        status='approved',
        quality_score=88,
        draft_text='Студия MAPPA официально подтвердила работу над третьим сезоном «Магической битвы».\\n\\nПремьера запланирована на 2027 год. Фанаты с нетерпением ждут продолжения истории Юдзи Итадори.\\n\\n#МагическаяБитва #JujutsuKaisen #MAPPA',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(post)
    db.commit()
    print(f'✅ Создан тестовый approved пост: {post.id}')
    print(f'   headline: {post.headline}')
    print(f'   image_url: {post.image_url}')
finally:
    db.close()