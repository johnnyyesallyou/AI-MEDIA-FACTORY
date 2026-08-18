import pathlib, py_compile

f = pathlib.Path('backend/automation/scheduler.py')
s = f.read_text(encoding='utf-8')

# 1. Добавляем import asyncio если нет
if 'import asyncio' not in s:
    s = s.replace(
        'import logging\nimport os',
        'import asyncio\nimport logging\nimport os'
    )
    print('Added: import asyncio')

# 2. Добавляем MonitoringJob импорт после существующих импортов
if 'MonitoringJob' not in s:
    # Ищем последний import в начале файла
    lines = s.split('\n')
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            last_import_idx = i
    lines.insert(last_import_idx + 1, 'from .jobs import MonitoringJob')
    s = '\n'.join(lines)
    print('Added: MonitoringJob import')

# 3. Добавляем monitoring job registration в метод start() после load_schedules_from_db
monitoring_registration = '''
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

if 'monitoring_job' not in s:
    # Ищем точное место: после load_schedules_from_db() и перед self.scheduler.start()
    s = s.replace(
        '        await self.load_schedules_from_db()\n\n        self.scheduler.start()',
        '        await self.load_schedules_from_db()\n' + monitoring_registration + '\n        self.scheduler.start()'
    )
    print('Added: monitoring job registration in start()')

f.write_text(s, encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('\n✅✅✅ scheduler.py валиден')
except py_compile.PyCompileError as e:
    print(f'\n❌ Ошибка: {e}')