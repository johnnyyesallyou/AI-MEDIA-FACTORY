import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from backend.automation.publishers.telegram import TelegramPublisher

db = SessionLocal()
try:
    # Находим контент с image_url
    content = db.query(ContentORM).filter(
        ContentORM.image_url.isnot(None),
        ContentORM.image_url != '',
        ContentORM.status == 'published'
    ).order_by(ContentORM.published_at.desc()).first()
    
    if not content:
        print('❌ Нет published контента с image_url')
        sys.exit(1)
    
    # Находим канал
    channel = db.query(ChannelORM).filter(ChannelORM.name.like('%Anime%')).first()
    
    print(f'Контент: {content.headline[:50]}')
    print(f'image_url: {content.image_url[:80]}...')
    print(f'Канал: {channel.name}')
    
    # Создаём publisher
    publisher = TelegramPublisher()
    credentials = {
        'bot_token': channel.bot_token,
        'chat_id': channel.chat_id
    }
    
    # Публикуем с image_url (не локальный файл)
    print('\\nПубликуем с image_url...')
    result = publisher.publish(
        text=f"{content.headline}\\n\\n{content.draft_text}",
        credentials=credentials,
        image_url=content.image_url  # Передаём URL напрямую
    )
    
    print(f'\\n✅ Результат:')
    print(f'   success: {result.success}')
    print(f'   message_id: {result.message_id}')
    if result.error:
        print(f'   error: {result.error}')
    
finally:
    db.close()