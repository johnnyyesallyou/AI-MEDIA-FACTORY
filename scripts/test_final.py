import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.asset.manager import AssetManager

db = SessionLocal()
try:
    content = db.query(ContentORM).filter(
        ContentORM.image_url.isnot(None),
        ContentORM.image_url != ''
    ).first()
    
    if not content:
        print('❌ Нет content с image_url')
        sys.exit(1)
    
    print(f'Используем: {content.headline[:50]}')
    print(f'  image_url: {content.image_url[:80]}...')
    print(f'  image_prompt: {content.image_prompt or "None"}')
    
    manager = AssetManager()
    
    print('\\nСкачиваем и сохраняем asset (может занять до 2 минут)...')
    asset = manager.save_from_url(
        image_url=content.image_url,
        content_id=content.id,
        prompt=content.image_prompt or 'anime poster',
        model='pollinations-flux',
        width=1024,
        height=576
    )
    
    if asset:
        print(f'\\n✅ Asset сохранён!')
        print(f'   id: {asset.id}')
        print(f'   storage_path: {asset.storage_path}')
        print(f'   public_url: {asset.public_url}')
        print(f'   generation_time_ms: {asset.generation_time_ms}')
        
        # Обновляем content.asset_id
        content.asset_id = asset.id
        db.commit()
        print(f'\\n✅ content.asset_id обновлён: {asset.id}')
    else:
        print('❌ Не удалось сохранить asset')
finally:
    db.close()