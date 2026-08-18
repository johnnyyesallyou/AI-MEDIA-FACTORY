import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from datetime import datetime

db = SessionLocal()
try:
    # Берём 10 самых старых approved постов (они публиковались первыми)
    approved = db.query(ContentORM).filter(
        ContentORM.channel_id == '4400626c-e53d-46fa-a49a-65791cb2948a',
        ContentORM.status == 'approved'
    ).order_by(ContentORM.created_at).limit(10).all()
    
    print(f'Обновляю статус для {len(approved)} постов...')
    
    for post in approved:
        post.status = 'published'
        post.published_at = datetime.utcnow()
        print(f'  Updated: {post.headline[:50]}')
    
    db.commit()
    print(f'✅ Обновлено {len(approved)} постов')
finally:
    db.close()