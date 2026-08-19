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
        source_url='https://test.com/one-piece',
        headline='One Piece: новый эпизод выходит в субботу',
        source_text='Toei Animation анонсировала новый эпизод',
        status='approved',
        quality_score=90,
        draft_text='Новый эпизод One Piece выходит в эту субботу. Фанаты ждут продолжения истории Луффи.',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(post)
    db.commit()
    print(f'✅ Создан пост: {post.id}')
    print(f'   headline: {post.headline}')
    print(f'   draft_text length: {len(post.draft_text)}')
finally:
    db.close()