import sys, asyncio
sys.path.insert(0, '/app')

from core.database import SessionLocal
from core.repositories.channel_repository import ChannelRepository
from core.models.content_orm import ContentORM
from backend.automation.publishers.factory import PublisherFactory
from backend.automation.jobs.automation_jobs import PublishJob

async def publish_approved():
    db = SessionLocal()
    try:
        # Находим approved контент для VK канала
        approved = db.query(ContentORM).filter(
            ContentORM.channel_id == '4400626c-e53d-46fa-a49a-65791cb2948a',
            ContentORM.status == 'approved'
        ).all()
        
        print(f'Найдено approved постов: {len(approved)}')
        
        if not approved:
            print('Нет approved постов — ищем draft с высоким quality')
            approved = db.query(ContentORM).filter(
                ContentORM.channel_id == '4400626c-e53d-46fa-a49a-65791cb2948a',
                ContentORM.status == 'draft',
                ContentORM.quality_score >= 70
            ).all()
            print(f'Найдено draft с quality >= 70: {len(approved)}')
        
        if not approved:
            print('Нет контента для публикации')
            return
        
        # Получаем канал
        repo = ChannelRepository(db)
        channel = repo.get('4400626c-e53d-46fa-a49a-65791cb2948a')
        
        # Берём первый approved пост
        post = approved[0]
        print(f'\\nПубликуем: {post.headline[:50]}...')
        print(f'  quality_score: {post.quality_score}')
        print(f'  text_length: {len(post.draft_text or "")}')
        
        # Создаём credentials для VK
        credentials = {
            'group_id': channel.vk_group_id,
            'access_token': channel.vk_access_token
        }
        
        # Получаем VkPublisher
        publisher = PublisherFactory.get('vk')
        print(f'Publisher: {publisher.__class__.__name__}')
        
        # Формируем полный текст поста
        full_text = f'{post.headline}\\n\\n{post.draft_text}'
        
        # Публикуем
        result = publisher.publish(
            text=full_text,
            credentials=credentials,
            channel=channel
        )
        
        print(f'\\n🎯 Результат:')
        print(f'  success: {result.success}')
        print(f'  message_id: {result.message_id}')
        print(f'  error: {result.error}')
        
        if result.success:
            post.status = 'published'
            post.published_at = result.published_at
            db.commit()
            print('\\n🎉 ПОСТ ОПУБЛИКОВАН В VK!')
    finally:
        db.close()

asyncio.run(publish_approved())