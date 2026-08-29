import sys, asyncio
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.post_generation_service import PostGenerationService
from engines.publish_service import PublishService

async def test():
    db = SessionLocal()
    try:
        # 1. Генерируем пост
        print("=== Шаг 1: Generate ===")
        gen_service = PostGenerationService(db)
        article = {
            "title": "Anthropic выпустила Claude 4",
            "source_name": "TechCrunch",
            "summary": "Anthropic анонсировала новую модель Claude 4 с улучшенными возможностями reasoning и безопасностью.",
            "image_url": "https://example.com/claude.jpg"
        }
        
        content = await gen_service.generate_post(
            channel_id="24df0f84-46c2-4df4-ab39-d76881b35438",
            content=article,
            content_type="news"
        )
        
        if not content:
            print("❌ Generation failed")
            return
            
        print(f"✅ Generated: id={content.id}")
        print(f"  Status: {content.status}")
        print(f"  Video: {'YES' if getattr(content, 'video_url', None) else 'NO'}")
        print(f"  Image: {'YES' if content.image_url else 'NO'}")
        print(f"  Text preview: {content.draft_text[:120]}...")
        
        # 2. Публикуем
        print("\n=== Шаг 2: Publish ===")
        pub_service = PublishService(db)
        published = await pub_service.publish_generated_post(content.id)
        
        if published:
            print(f"✅ Published: message_id={published.telegram_message_id}")
            print(f"  Status: {published.status}")
            print(f"  Published at: {published.published_at}")
        else:
            print(f"❌ Publish failed: {content.publish_error}")
            return
        
        # 3. Проверяем PostHistory
        print("\n=== Шаг 3: PostHistory ===")
        from core.models.post_history_orm import PostHistoryORM
        posts = db.query(PostHistoryORM).filter(
            PostHistoryORM.channel_id == "24df0f84-46c2-4df4-ab39-d76881b35438"
        ).order_by(PostHistoryORM.created_at.desc()).limit(2).all()
        
        print(f"✅ Recent posts in history: {len(posts)}")
        for p in posts:
            print(f"  - id={p.id[:18]}... media={p.media_type} msg_id={p.message_id}")
        
        print("\n🎉 ПОЛНЫЙ ЦИКЛ ПРОЙДЕН!")
        print("   Generate (LLM + Pixabay)")
        print("   → ContentORM (status=generated)")
        print("   → Publish (Telegram sendVideo)")
        print("   → ContentORM (status=published + message_id)")
        print("   → PostHistoryORM (для analytics)")
        
    finally:
        db.close()

asyncio.run(test())