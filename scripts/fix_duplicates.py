import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8')

# Удаляем дубликаты импортов, которые попали внутрь try-блока
duplicates = [
    '            from core.models.channel_schedule_orm import ChannelScheduleORM',
    '            from core.models.content_orm import ContentORM',
    '        from core.models.channel_schedule_orm import ChannelScheduleORM',
    '        from core.models.content_orm import ContentORM',
]

for dup in duplicates:
    if dup in s:
        s = s.replace(dup + '\n', '')
        print(f'OK: removed duplicate: {dup.strip()}')

p.write_text(s, encoding='utf-8')
print('DONE')