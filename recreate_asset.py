import sys
sys.path.insert(0, '/app')
import os

# Убеждаемся что директория существует
os.makedirs('/app/assets/2026/08', exist_ok=True)
print(f'Директория создана: {os.path.exists("/app/assets/2026/08")}')
print(f'Права: {oct(os.stat("/app/assets/2026/08").st_mode)}')

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
    
    manager = AssetManager()
    
    print('\\nСкачиваем и сохраняем asset...')
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
        
        # Проверяем файл физически
        full_path = f"/app/{asset.storage_path}"
        print(f'   Файл существует: {os.path.exists(full_path)}')
        if os.path.exists(full_path):
            print(f'   Размер: {os.path.getsize(full_path)} bytes')
            print(f'   Права: {oct(os.stat(full_path).st_mode)}')
        
        content.asset_id = asset.id
        db.commit()
    else:
        print('❌ Не удалось сохранить')
finally:
    db.close()