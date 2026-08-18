import pathlib, py_compile

f = pathlib.Path('backend/automation/scheduler.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем метод add_channel_job и полностью его перезаписываем
new_lines = []
i = 0
skip_until_next_method = False

while i < len(lines):
    line = lines[i]
    
    # Начало метода add_channel_job
    if 'async def add_channel_job(self, schedule: ChannelScheduleORM):' in line:
        # Добавляем заголовок метода
        new_lines.append(line)
        i += 1
        
        # Добавляем docstring
        if i < len(lines) and '"""' in lines[i]:
            new_lines.append(lines[i])
            i += 1
            # Добавляем остальные строки docstring
            while i < len(lines) and '"""' not in lines[i]:
                new_lines.append(lines[i])
                i += 1
            if i < len(lines):
                new_lines.append(lines[i])  # закрывающая """
                i += 1
        
        # Добавляем правильную реализацию
        new_lines.append('        if not self.scheduler:')
        new_lines.append('            return')
        new_lines.append('')
        new_lines.append('        job_id = f"channel_{schedule.channel_id}"')
        new_lines.append('')
        new_lines.append('        # Удаляем старую задачу, если она существует')
        new_lines.append('        existing_job = self.scheduler.get_job(job_id)')
        new_lines.append('        if existing_job:')
        new_lines.append('            self.scheduler.remove_job(job_id)')
        new_lines.append('')
        new_lines.append('        try:')
        new_lines.append('            # Парсим cron-выражение')
        new_lines.append('            tz = pytz_timezone(schedule.timezone or "Europe/Moscow")')
        new_lines.append('            trigger = CronTrigger.from_crontab(schedule.cron_expression, timezone=tz)')
        new_lines.append('')
        new_lines.append('            # Добавляем задачу')
        new_lines.append('            self.scheduler.add_job(')
        new_lines.append('                self.run_channel_automation,')
        new_lines.append('                trigger=trigger,')
        new_lines.append('                args=[schedule.channel_id],')
        new_lines.append('                id=job_id,')
        new_lines.append('                name=f"Automation for channel {schedule.channel_id}",')
        new_lines.append('                replace_existing=True')
        new_lines.append('            )')
        new_lines.append('')
        new_lines.append('            logger.info(')
        new_lines.append('                "Added job for channel %s with cron \'%s\'",')
        new_lines.append('                schedule.channel_id,')
        new_lines.append('                schedule.cron_expression')
        new_lines.append('            )')
        new_lines.append('')
        new_lines.append('        except Exception as e:')
        new_lines.append('            logger.error(')
        new_lines.append('                "Failed to add job for channel %s: %s",')
        new_lines.append('                schedule.channel_id,')
        new_lines.append('                e')
        new_lines.append('            )')
        new_lines.append('')
        
        # Пропускаем старый метод до следующего метода
        while i < len(lines):
            if lines[i].strip().startswith('async def ') and 'add_channel_job' not in lines[i]:
                # Нашли следующий метод
                break
            if lines[i].strip().startswith('def ') and 'add_channel_job' not in lines[i]:
                # Нашли следующий метод (не async)
                break
            i += 1
        
        print('✅ Метод add_channel_job полностью перезаписан')
        continue
    
    new_lines.append(line)
    i += 1

f.write_text('\n'.join(new_lines), encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ scheduler.py валиден')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')