import pathlib
p = pathlib.Path('./backend/app/api/v1/channels.py')
s = p.read_text(encoding='utf-8')

# Заменяем функцию _schedule_to_response
old_func = '''def _schedule_to_response(s: ChannelScheduleORM) -> ChannelScheduleResponse:
    return ChannelScheduleResponse(
        id=s.id,
        channel_id=s.channel_id,
        cron_expression=s.cron_expression,
        timezone=s.timezone,
        max_posts_per_day=s.max_posts_per_day,
        auto_publish=s.auto_publish,
        is_active=s.is_active,
        last_run=s.last_run,
        next_run=s.next_run,
    )'''

new_func = '''def _schedule_to_response(s: ChannelScheduleORM) -> ChannelScheduleResponse:
    # Берём next_run из живого APScheduler, а не из БД
    next_run = automation_scheduler.get_next_run(s.channel_id)
    return ChannelScheduleResponse(
        id=s.id,
        channel_id=s.channel_id,
        cron_expression=s.cron_expression,
        timezone=s.timezone,
        max_posts_per_day=s.max_posts_per_day,
        auto_publish=s.auto_publish,
        is_active=s.is_active,
        last_run=s.last_run,
        next_run=next_run,
    )'''

if old_func in s:
    s = s.replace(old_func, new_func)
    p.write_text(s, encoding='utf-8')
    print('✅ _schedule_to_response теперь берёт next_run из APScheduler')
else:
    print('❌ Старая функция не найдена')