import pathlib, py_compile

f = pathlib.Path('backend/automation/scheduler.py')
lines = f.read_text(encoding='utf-8').split('\n')
print(f'Total lines: {len(lines)}')

# Показываем проблемную область
print('\n=== Lines 105-125 ===')
for i in range(104, min(125, len(lines))):
    print(f'{i+1:4d}: {lines[i]}')

# Стратегия: находим строку "scheduler.add_job(" (с маленькой s - это сломанный глобальный)
# и удаляем весь блок до закрывающей скобки
new_lines = []
skip = False
paren_depth = 0
i = 0
removed_count = 0
while i < len(lines):
    line = lines[i]
    
    # Детектируем начало сломанного блока (scheduler.add_job - с маленькой s, глобальный)
    if line.strip().startswith('scheduler.add_job(') and not skip:
        skip = True
        paren_depth = line.count('(') - line.count(')')
        removed_count += 1
        print(f'  Removing line {i+1}: {line.strip()[:60]}')
        i += 1
        continue
    
    if skip:
        paren_depth += line.count('(') - line.count(')')
        removed_count += 1
        print(f'  Removing line {i+1}: {line.strip()[:60]}')
        if paren_depth <= 0:
            skip = False
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

print(f'\nRemoved {removed_count} lines')

# Теперь добавляем правильные импорты и monitoring job
s = '\n'.join(new_lines)

# Добавляем import asyncio если нет
if 'import asyncio' not in s:
    s = s.replace('import logging\nimport os', 'import asyncio\nimport logging\nimport os')
    print('Added: import asyncio')

# Добавляем MonitoringJob импорт
if 'MonitoringJob' not in s:
    s = s.replace(
        'from .automation_manager_v2 import automation_manager_v2',
        'from .automation_manager_v2 import automation_manager_v2\nfrom .jobs import MonitoringJob'
    )
    print('Added: MonitoringJob import')

# Добавляем monitoring job в start() - после load_schedules_from_db
monitoring_block = '''
        # Sprint 12: Monitoring job (every 10 minutes)
        self.scheduler.add_job(
            func=lambda: asyncio.to_thread(MonitoringJob().run),
            trigger="interval",
            minutes=10,
            id="monitoring_job",
            name="Monitoring (health + SLA)",
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )
        logger.info("Added monitoring job (every 10 minutes)")
'''

if 'monitoring_job' not in s and 'await self.load_schedules_from_db()' in s:
    s = s.replace(
        '        await self.load_schedules_from_db()\n\n        self.scheduler.start()',
        '        await self.load_schedules_from_db()\n' + monitoring_block + '\n        self.scheduler.start()'
    )
    print('Added: monitoring job registration in start()')

f.write_text(s, encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('\n✅✅✅ scheduler.py валиден')
except py_compile.PyCompileError as e:
    print(f'\n❌ Ошибка: {e}')
    # Показываем проблемные строки
    lines_check = s.split('\n')
    for i, line in enumerate(lines_check, 1):
        if 'scheduler.add_job' in line and 'self.' not in line:
            print(f'  Problem line {i}: {line}')