import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.content_orm import ContentORM
from backend.automation.publishers.telegram import TelegramPublisher

db = SessionLocal()
try:
    # Берём ОДИН approved пост с image_url
    post = db.query(ContentORM).filter(
        ContentORM.id == 'be52f1da-4be0-424d-8834-6e274f334eb9'
    ).first()
    
    if not post:
        print('❌ Пост не найден')
        sys.exit(1)
    
    # Канал
    channel = db.query(ChannelORM).filter(ChannelORM.name.like('%Anime%')).first()
    
    print(f'Пост: {post.headline}')
    print(f'image_url: {post.image_url}')
    print(f'Канал: {channel.name}')
    
    publisher = TelegramPublisher()
    credentials = {
        'bot_token': channel.bot_token,
        'chat_id': channel.chat_id
    }
    
    full_text = f"{post.headline}\n\n{post.draft_text}"
    
    print(f'\\nПубликуем с картинкой...')
    result = publisher.publish(
        text=full_text,
        credentials=credentials,
        image_url=post.image_url
    )
    
    print(f'\\n=== Результат ===')
    print(f'   success: {result.success}')
    print(f'   message_id: {result.message_id}')
    if result.error:
        print(f'   error: {result.error}')
    print(f'   platform_data: {result.platform_data}')
finally:
    db.close()