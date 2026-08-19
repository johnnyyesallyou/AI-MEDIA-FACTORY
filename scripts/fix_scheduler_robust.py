import pathlib, py_compile

f = pathlib.Path('backend/automation/scheduler.py')
content = f.read_text(encoding='utf-8')

# 1. Находим и полностью перезаписываем сломанный метод add_channel_job
start_marker = "async def add_channel_job(self, schedule: ChannelScheduleORM):"
end_marker = "async def run_channel_automation(self, channel_id: str):"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    method_header = content[start_idx:content.find("\n", start_idx) + 1]
    
    new_method_body = '''        """Добавляет задачу для конкретного канала на основе его cron-расписания."""
        if not self.scheduler:
            return

        job_id = f"channel_{schedule.channel_id}"

        # Удаляем старую задачу, если она существует
        existing_job = self.scheduler.get_job(job_id)
        if existing_job:
            self.scheduler.remove_job(job_id)

        try:
            # Парсим cron-выражение
            tz = pytz_timezone(schedule.timezone or "Europe/Moscow")
            trigger = CronTrigger.from_crontab(schedule.cron_expression, timezone=tz)

            # Добавляем задачу
            self.scheduler.add_job(
                self.run_channel_automation,
                trigger=trigger,
                args=[schedule.channel_id],
                id=job_id,
                name=f"Automation for channel {schedule.channel_id}",
                replace_existing=True
            )

            logger.info(
                "Added job for channel %s with cron '%s'",
                schedule.channel_id,
                schedule.cron_expression
            )

        except Exception as e:
            logger.error(
                "Failed to add job for channel %s: %s",
                schedule.channel_id,
                e
            )

'''
    
    # Собираем файл заново
    content = content[:start_idx] + method_header + new_method_body + "    " + content[end_idx:]
    print('✅ Метод add_channel_job полностью перезаписан чистой версией')
else:
    print('⚠️ Не удалось найти границы метода add_channel_job')

# 2. Добавляем import asyncio
if 'import asyncio' not in content:
    content = content.replace('import logging\nimport os', 'import asyncio\nimport logging\nimport os')
    print('✅ Добавлен import asyncio')

# 3. Добавляем MonitoringJob импорт
if 'MonitoringJob' not in content:
    content = content.replace(
        'from .automation_manager_v2 import automation_manager_v2',
        'from .automation_manager_v2 import automation_manager_v2\nfrom .jobs import MonitoringJob'
    )
    print('✅ Добавлен import MonitoringJob')

# 4. Добавляем monitoring job в start()
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

if 'monitoring_job' not in content:
    content = content.replace(
        '        await self.load_schedules_from_db()\n\n        self.scheduler.start()',
        '        await self.load_schedules_from_db()\n' + monitoring_block + '\n        self.scheduler.start()'
    )
    print('✅ Добавлен monitoring job в start()')

f.write_text(content, encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('\n✅✅✅ scheduler.py валиден')
except py_compile.PyCompileError as e:
    print(f'\n❌ Ошибка: {e}')