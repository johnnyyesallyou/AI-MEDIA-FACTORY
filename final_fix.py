import pathlib, re

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')

# Удаляем строки без отступов (начинаются с колонки 0) в любом месте
# Это те самые дубликаты, которые случайно попали внутрь try-блока
lines = s.split('\n')
new_lines = []
removed = 0
for i, line in enumerate(lines, 1):
    # Строки без отступов, которые являются импортами channel_schedule_orm или content_orm
    if line.startswith('from core.models.channel_schedule_orm import'):
        print(f"  REMOVE line {i}: {line}")
        removed += 1
        continue
    if line.startswith('from core.models.content_orm import'):
        print(f"  REMOVE line {i}: {line}")
        removed += 1
        continue
    new_lines.append(line)

print(f'Removed {removed} duplicate import lines')

# Проверяем, что глобальные импорты в начале файла остались
if 'from core.models.channel_schedule_orm import ChannelScheduleORM' not in '\n'.join(new_lines[:30]):
    print('WARN: global import missing from top, re-adding...')
    # Добавляем после from core.repositories.channel_repository import ChannelRepository
    for i, line in enumerate(new_lines):
        if line.strip() == 'from core.repositories.channel_repository import ChannelRepository':
            new_lines.insert(i+1, 'from core.models.channel_schedule_orm import ChannelScheduleORM')
            new_lines.insert(i+2, 'from core.models.content_orm import ContentORM')
            break

s = '\n'.join(new_lines)
p.write_text(s, encoding='utf-8')
print('DONE')