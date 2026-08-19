import pathlib
p = pathlib.Path('./backend/automation/scheduler.py')
s = p.read_text(encoding='utf-8')

if 'async def get_next_run' not in s:
    new_method = '''
    def get_next_run(self, channel_id: str):
        """Возвращает next_run для конкретного канала из APScheduler."""
        if not self.scheduler:
            return None
        job_id = f"channel_{channel_id}"
        job = self.scheduler.get_job(job_id)
        return job.next_run_time if job else None

'''
    # Вставляем метод перед def refresh_schedule
    if 'async def refresh_schedule' in s:
        s = s.replace('    async def refresh_schedule', new_method + '    async def refresh_schedule')
        p.write_text(s, encoding='utf-8')
        print('✅ Добавлен метод get_next_run в AutomationScheduler')
    else:
        print('❌ Не найден якорь refresh_schedule')
else:
    print('ℹ️ Метод get_next_run уже существует')