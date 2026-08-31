import sys, asyncio
sys.path.insert(0, '/app')

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.evaluator.engine import EvaluatorEngine

async def evaluate_drafts():
    db = SessionLocal()
    try:
        # Находим все draft посты для VK канала
        drafts = db.query(ContentORM).filter(
            ContentORM.channel_id == '4400626c-e53d-46fa-a49a-65791cb2948a',
            ContentORM.status == 'draft'
        ).all()
        
        print(f'Найдено draft постов для оценки: {len(drafts)}')
        
        evaluator = EvaluatorEngine()
        
        for i, post in enumerate(drafts, 1):
            print(f'\\n[{i}/{len(drafts)}] Оцениваю: {post.headline[:50]}...')
            print(f'  text_length: {len(post.draft_text or "")}')
            
            try:
                # Оцениваем пост
                result = await evaluator.evaluate(
                    text=post.draft_text,
                    headline=post.headline,
                    channel=None
                )
                
                post.quality_score = result.get('score', 0)
                post.evaluation_notes = result.get('notes', '')
                
                # Если score >= 70 — помечаем как approved
                if post.quality_score >= 70:
                    post.status = 'approved'
                    print(f'  ✅ APPROVED! score={post.quality_score}')
                else:
                    print(f'  ⚠️ score={post.quality_score} (ниже порога 70)')
                
            except Exception as e:
                print(f'  ❌ Ошибка оценки: {e}')
        
        db.commit()
        print(f'\\n✅ Оценка завершена! Обновлено {len(drafts)} постов')
    finally:
        db.close()

asyncio.run(evaluate_drafts())