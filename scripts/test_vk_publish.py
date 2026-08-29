import sys, asyncio
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from engines.post_generation_service import PostGenerationService
from engines.publish_service import PublishService

async def test():
    db = SessionLocal()
    try:
        # 1. Найти VK канал
        vk_channel = db.query(ChannelORM).filter(ChannelORM.platform == "vk").first()
        if not vk_channel:
            print("❌ VK channel not found")
            return
        
        print("=" * 70)
        print("VK PUBLISH E2E TEST")
        print("=" * 70)
        print(f"\nVK Channel: {vk_channel.name}")
        print(f"  ID: {vk_channel.id}")
        print(f"  Platform: {vk_channel.platform}")
        print(f"  Group ID: {vk_channel.vk_group_id}")
        
        # 2. Генерируем пост
        print("\n[1] Generate post...")
        gen_service = PostGenerationService(db)
        article = {
            "title": "AI Media Factory теперь публикует в VK!",
            "source_name": "AI Media Factory",
            "summary": "Запущена интеграция с VK. Теперь система может автоматически публиковать посты в группы ВКонтакте.",
        }
        
        content = await gen_service.generate_post(
            channel_id=vk_channel.id,
            content=article,
            content_type="news"
        )
        
        if not content:
            print("❌ Generation failed")
            return
        
        print(f"✅ Generated: id={content.id}")
        print(f"  Status: {content.status}")
        print(f"  Text: {content.draft_text[:150]}...")
        
        # 3. Публикуем в VK
        print("\n[2] Publish to VK...")
        pub_service = PublishService(db)
        published = await pub_service.publish_generated_post(content.id)
        
        if published:
            print(f"✅ Published to VK!")
            print(f"   VK Post ID: {published.telegram_message_id}")
            print(f"   Status: {published.status}")
            print(f"   Published at: {published.published_at}")
            
            # 4. Проверяем PostHistory
            print("\n[3] Verify PostHistory...")
            from core.models.post_history_orm import PostHistoryORM
            from sqlalchemy import desc
            
            history = db.query(PostHistoryORM)\
                .filter(PostHistoryORM.channel_id == vk_channel.id)\
                .order_by(desc(PostHistoryORM.posted_at))\
                .first()
            
            if history:
                print(f"✅ PostHistory recorded:")
                print(f"   ID: {history.id}")
                print(f"   Platform: {history.platform}")
                print(f"   Message ID: {history.message_id}")
                print(f"   Posted at: {history.posted_at}")
            
            print("\n" + "=" * 70)
            print("🎉 VK E2E TEST PASSED!")
            print("   Generate → Publish (VK) → PostHistory")
            print("=" * 70)
        else:
            print(f"❌ Publish failed: {content.publish_error}")
        
    finally:
        db.close()

asyncio.run(test())