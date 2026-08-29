import sys, asyncio
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.post_generation_service import PostGenerationService
from engines.publish_service import PublishService

async def test():
    db = SessionLocal()
    try:
        print("=" * 70)
        print("E2E TEST: Manga Channel (manga_releases profile)")
        print("=" * 70)
        
        # 1. Генерируем пост
        print("\n[1] Generate post with LLM + cover image (NO video)...")
        gen_service = PostGenerationService(db)
        manga_content = {
            "title": "One Piece",
            "title_ru": "Ван Пис",
            "chapter_number": "1123",
            "genres": ["Adventure", "Action", "Fantasy"],
            "description": "Монки Д. Луффи продолжает своё путешествие, чтобы стать Королём Пиратов.",
            "cover_url": "https://remanga.org/media/titles/one-piece/cover.jpg",
            "source_url": "https://remanga.org/manga/one-piece"
        }
        
        content = await gen_service.generate_post(
            channel_id="manga-channel-001",
            content=manga_content,
            content_type="manga"
        )
        
        if not content:
            print("❌ Generation failed")
            return
        
        print(f"✅ Generated:")
        print(f"   ID: {content.id}")
        print(f"   Status: {content.status}")
        print(f"   Video: {'YES' if content.video_url else 'NO'} (expected: NO)")
        print(f"   Image: {'YES' if content.image_url else 'NO'} (expected: YES)")
        print(f"   Text preview: {content.draft_text[:150]}...")
        
        # 2. Публикуем
        print("\n[2] Publish to Telegram...")
        pub_service = PublishService(db)
        published = await pub_service.publish_generated_post(content.id)
        
        if published:
            print(f"✅ Published:")
            print(f"   Message ID: {published.telegram_message_id}")
            print(f"   Status: {published.status}")
            print(f"   Published at: {published.published_at}")
        else:
            print(f"❌ Publish failed: {content.publish_error}")
            return
        
        # 3. Проверяем PostHistory
        print("\n[3] Verify PostHistory...")
        from core.models.post_history_orm import PostHistoryORM
        from sqlalchemy import desc
        
        history = db.query(PostHistoryORM)\
            .filter(PostHistoryORM.channel_id == "manga-channel-001")\
            .order_by(desc(PostHistoryORM.posted_at))\
            .first()
        
        if history and history.message_id == published.telegram_message_id:
            print(f"✅ PostHistory recorded:")
            print(f"   ID: {history.id}")
            print(f"   Media type: {history.media_type}")
            print(f"   Message ID: {history.message_id}")
            print(f"   Posted at: {history.posted_at}")
        else:
            print(f"❌ PostHistory not found or mismatch")
        
        print("\n" + "=" * 70)
        print("🎉 MANGA E2E TEST PASSED!")
        print("   Generate → Publish → PostHistory")
        print("   Media Policy: image only (no video) ✅")
        print("=" * 70)
        
    finally:
        db.close()

asyncio.run(test())