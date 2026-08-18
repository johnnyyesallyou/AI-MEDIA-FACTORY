import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from datetime import datetime

db = SessionLocal()
try:
    anime_channel = db.query(ChannelORM).filter(ChannelORM.name.like('%Anime%')).first()
    
    post = ContentORM(
        channel_id=anime_channel.id,
        source_url='https://test.com/solo-leveling-final',
        headline='Solo Leveling: финальный сезон выходит в 2026',
        source_text='A-1 Pictures анонсировала финальный сезон Solo Leveling',
        status='approved',
        quality_score=92,
        draft_text='Студия A-1 Pictures официально подтвердила работу над финальным сезоном Solo Leveling. Премьера запланирована на весну 2026 года.',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(post)
    db.commit()
    print(f'✅ Создан тестовый post: {post.id}')
finally:
    db.close()