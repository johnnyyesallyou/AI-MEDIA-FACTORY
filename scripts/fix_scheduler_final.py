import pathlib, py_compile

f = pathlib.Path('backend/automation/scheduler.py')
s = f.read_text(encoding='utf-8')

# 1. Убираем вставленный monitoring job из неправильного места
broken_block = '''            # Р"РѕР±Р°РІР»СЏРµРј Р·Р°РґР°С‡Сѓ
            self.scheduler.add_job(

            # Sprint 12: Monitoring job (every 10 minutes)
            scheduler.add_job(
                func=lambda: asyncio.to_thread(MonitoringJob().run),
                trigger="interval",
                minutes=10,
                id="monitoring_job",
                name="Monitoring (health + SLA)",
                replace_existing=True,
                max_instances=1,
                coalesce=True
            )

                self.run_channel_automation,'''

fixed_block = '''            # Р"РѕР±Р°РІР»СЏРµРј Р·Р°РґР°С‡Сѓ
            self.scheduler.add_job(
                self.run_channel_automation,'''

if broken_block in s:
    s = s.replace(broken_block, fixed_block, 1)
    print('  ✅ Убран сломанный блок из add_channel_job')
else:
    print('  ⚠️ Сломанный блок не найден (возможно уже исправлен)')

# 2. Добавляем импорт asyncio
if 'import asyncio' not in s:
    s = s.replace(
        'import logging\nimport os',
        'import asyncio\nimport logging\nimport os'
    )
    print('  ✅ Добавлен import asyncio')

# 3. Добавляем импорт MonitoringJob (если ещё нет)
if 'MonitoringJob' not in s:
    # Находим импорт jobs
    if 'from .jobs import' in s:
        # Добавляем в строку импорта
        import_line = [line for line in s.split('\n') if 'from .jobs import' in line][0]
        if 'MonitoringJob' not in import_line:
            new_import = import_line.rstrip() + ', MonitoringJob'
            s = s.replace(import_line, new_import, 1)
            print(f'  ✅ Добавлен MonitoringJob в импорт')
    else:
        # Добавляем новый импорт после других импортов
        s = s.replace(
            'from .automation_manager_v2 import automation_manager_v2',
            'from .automation_manager_v2 import automation_manager_v2\nfrom .jobs import MonitoringJob'
        )
        print('  ✅ Добавлен import MonitoringJob')

# 4. Добавляем monitoring job в start() метод (после load_schedules_from_db)
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

if 'monitoring_job' not in s and 'load_schedules_from_db()' in s:
    s = s.replace(
        '        await self.load_schedules_from_db()\n\n        self.scheduler.start()',
        '        await self.load_schedules_from_db()\n' + monitoring_registration + '\n        self.scheduler.start()'
    )
    print('  ✅ Добавлен monitoring job в start()')

f.write_text(s, encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('  ✅✅✅ scheduler.py валиден')
except py_compile.PyCompileError as e:
    print(f'  ❌ Ошибка: {e}')