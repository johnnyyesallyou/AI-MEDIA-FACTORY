import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from datetime import datetime

db = SessionLocal()
try:
    # Создаём тестовый пост
    post = ContentORM(
        channel_id='4400626c-e53d-46fa-a49a-65791cb2948a',
        headline='🎉 Sprint 11: AI Media Factory публикует в VK!',
        draft_text='Это тестовый пост для проверки рефакторинга PublishJob.\\n\\nТеперь PublishJob использует готовый draft_text вместо повторной генерации через LLM. Это быстрее, дешевле и сохраняет согласованный текст который одобрил EvaluatorJob.\\n\\n#AI #MediaFactory #Sprint11 #VK',
        source_text='Manual test post',
        status='approved',
        quality_score=95,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(post)
    db.commit()
    print(f'✅ Создан тестовый approved пост: {post.id}')
    print(f'   headline: {post.headline}')
    print(f'   text_length: {len(post.draft_text)}')
finally:
    db.close()