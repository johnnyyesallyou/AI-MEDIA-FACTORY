import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')

# 1. Добавляем импорты ChannelScheduleORM и ContentORM
imports = '''from core.models.channel_schedule_orm import ChannelScheduleORM
from core.models.content_orm import ContentORM
'''
if 'from core.models.channel_schedule_orm' not in s:
    s = s.replace(
        'from core.repositories.channel_repository import ChannelRepository',
        'from core.repositories.channel_repository import ChannelRepository\n' + imports.strip()
    )
    print('OK: imports added')

# 2. Вставляем блок rate limits после "db = SessionLocal()"
old_block = '''        logger.info("PublishJob started")

        db = SessionLocal()

        published = 0
        failed = 0'''

new_block = '''        logger.info("PublishJob started")

        db = SessionLocal()

        # === RATE LIMITS & AUTO_PUBLISH ===
        schedule = None
        if channel:
            schedule = db.query(ChannelScheduleORM).filter(
                ChannelScheduleORM.channel_id == channel.id
            ).first()

        auto_publish = schedule.auto_publish if schedule else True
        max_posts_per_day = schedule.max_posts_per_day if schedule else 3

        if not auto_publish:
            logger.info("Auto-publish disabled for channel %s", channel.id if channel else None)
            p_logger.finish("success", details="Auto-publish disabled for this channel")
            db.close()
            return {"status": "skipped", "reason": "auto_publish_disabled", "published": 0, "failed": 0}

        # Считаем публикации за сегодня для этого канала
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        published_today = 0
        if channel:
            published_today = db.query(ContentORM).filter(
                ContentORM.channel_id == channel.id,
                ContentORM.status == "published",
                ContentORM.published_at >= today_start
            ).count()

        remaining = max(0, max_posts_per_day - published_today)
        logger.info(
            "Rate limit check: channel=%s published_today=%s max=%s remaining=%s",
            channel.id if channel else None, published_today, max_posts_per_day, remaining
        )

        if remaining <= 0:
            logger.info("Rate limit reached for channel %s", channel.id if channel else None)
            p_logger.finish(
                "success",
                details=f"Rate limit reached ({published_today}/{max_posts_per_day} posts today)"
            )
            db.close()
            return {
                "status": "skipped",
                "reason": "rate_limit",
                "published_today": published_today,
                "max_posts_per_day": max_posts_per_day,
                "published": 0,
                "failed": 0,
            }

        published = 0
        failed = 0'''

if old_block in s:
    s = s.replace(old_block, new_block)
    print('OK: rate limit block inserted')
else:
    print('ERROR: anchor block not found — покажем реальный текст:')
    idx = s.find('logger.info("PublishJob started")')
    if idx != -1:
        print(s[idx:idx+300])

# 3. Ограничиваем количество items оставшимися слотами
old_items = '''            items = content_repo.list_all(
                status="approved",
                limit=10
            )'''
new_items = '''            items = content_repo.list_all(
                status="approved",
                limit=min(10, remaining)
            )'''
if old_items in s:
    s = s.replace(old_items, new_items)
    print('OK: items list capped by remaining slots')
else:
    print('WARN: items limit pattern not found')

p.write_text(s, encoding='utf-8')
print('DONE')