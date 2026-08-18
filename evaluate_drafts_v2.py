import sys, asyncio
sys.path.insert(0, '/app')

from core.database import SessionLocal
from core.models.content_orm import ContentORM
# Пробуем разные варианты импорта
try:
    from engines.evaluator.engine import Evaluator
    evaluator_cls = Evaluator
    print('Используем: Evaluator')
except ImportError:
    try:
        from engines.evaluator.engine import EvaluatorEngine as Evaluator
        evaluator_cls = Evaluator
        print('Используем: EvaluatorEngine')
    except ImportError:
        from backend.engines.evaluator.engine import Evaluator
        evaluator_cls = Evaluator
        print('Используем: backend.engines.evaluator.Evaluator')

from backend.automation.jobs.automation_jobs import EvaluatorJob

async def evaluate_drafts():
    db = SessionLocal()
    try:
        # Находим все draft посты для VK канала
        drafts = db.query(ContentORM).filter(
            ContentORM.channel_id == '4400626c-e53d-46fa-a49a-65791cb2948a',
            ContentORM.status == 'draft'
        ).all()
        
        print(f'Найдено draft постов для оценки: {len(drafts)}')
        
        if not drafts:
            print('Нет постов для оценки')
            return
        
        evaluator = evaluator_cls()
        
        for i, post in enumerate(drafts, 1):
            print(f'\\n[{i}/{len(drafts)}] Оцениваю: {post.headline[:50]}...')
            print(f'  text_length: {len(post.draft_text or "")}')
            
            try:
                # Вызываем evaluate (синхронно или асинхронно)
                if hasattr(evaluator, 'evaluate'):
                    result = evaluator.evaluate(
                        text=post.draft_text,
                        headline=post.headline,
                        channel=None
                    )
                    if asyncio.iscoroutine(result):
                        result = await result
                elif hasattr(evaluator, 'evaluate_content'):
                    result = evaluator.evaluate_content(post)
                    if asyncio.iscoroutine(result):
                        result = await result
                else:
                    # Пробуем вызвать как функцию
                    result = evaluator(post.draft_text, post.headline)
                    if asyncio.iscoroutine(result):
                        result = await result
                
                # Парсим результат
                score = 0
                notes = ''
                if isinstance(result, dict):
                    score = result.get('score', result.get('quality_score', 0))
                    notes = result.get('notes', result.get('feedback', ''))
                elif hasattr(result, 'score'):
                    score = result.score
                    notes = getattr(result, 'notes', '')
                
                post.quality_score = score
                post.evaluation_notes = notes
                
                # Если score >= 70 — помечаем как approved
                if score >= 70:
                    post.status = 'approved'
                    print(f'  ✅ APPROVED! score={score}')
                else:
                    post.status = 'needs_revision'
                    print(f'  ⚠️ score={score} (needs_revision)')
                
            except Exception as e:
                print(f'  ❌ Ошибка оценки: {e}')
                import traceback
                traceback.print_exc()
        
        db.commit()
        print(f'\\n✅ Оценка завершена! Обновлено {len(drafts)} постов')
        
        # Статистика
        approved = len([p for p in drafts if p.status == 'approved'])
        print(f'   Approved: {approved}/{len(drafts)}')
        
    finally:
        db.close()

asyncio.run(evaluate_drafts())