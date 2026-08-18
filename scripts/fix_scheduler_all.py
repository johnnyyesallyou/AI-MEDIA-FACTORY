import pathlib
import re

p = pathlib.Path('./backend/automation/scheduler.py')
s = p.read_text(encoding='utf-8')
changes = []

# ФИКС 1: Удаляем дубликат logger = logging.getLogger(__name__)
# Подсчитываем сколько раз встречается
logger_lines = s.count('logger = logging.getLogger(__name__)')
if logger_lines > 1:
    # Удаляем все вхождения кроме первого
    first_occurrence = True
    lines = s.split('\n')
    new_lines = []
    for line in lines:
        if line.strip() == 'logger = logging.getLogger(__name__)':
            if first_occurrence:
                new_lines.append(line)
                first_occurrence = False
            else:
                # Пропускаем дубликат
                continue
        else:
            new_lines.append(line)
    s = '\n'.join(new_lines)
    changes.append(f'removed {logger_lines - 1} duplicate logger lines')

# ФИКС 2: Патчим start() - добавляем запуск v2 manager
old_start = '''    async def start(self):
        if self.scheduler and self.scheduler.running:
            logger.info("Automation scheduler already running")
            return

        logger.info("Automation scheduler starting with APScheduler...")
        print("🔥 Automation scheduler (APScheduler) starting", flush=True)

        self.scheduler = AsyncIOScheduler()'''

new_start = '''    async def start(self):
        if self.scheduler and self.scheduler.running:
            logger.info("Automation scheduler already running")
            return

        logger.info("Automation scheduler starting with APScheduler...")
        print("🔥 Automation scheduler (APScheduler) starting", flush=True)

        # Запускаем AutomationManager v2 если feature flag включен
        if USE_AUTOMATION_V2:
            logger.info("Starting AutomationManager v2 (Channel Isolation + Policies)...")
            print("🚀 AutomationManager v2 ENABLED (Channel Isolation + Policies)", flush=True)
            await automation_manager_v2.start()
        else:
            logger.info("Using legacy AutomationManager (v1)")
            print("ℹ️ Using legacy AutomationManager (v1). Set USE_AUTOMATION_V2=true to enable v2", flush=True)

        self.scheduler = AsyncIOScheduler()'''

if old_start in s and 'AutomationManager v2 ENABLED' not in s:
    s = s.replace(old_start, new_start, 1)
    changes.append('patched start() with v2 manager launch')
elif 'AutomationManager v2 ENABLED' in s:
    changes.append('start() already patched')

# ФИКС 3: Патчим stop() - добавляем остановку v2 manager
old_stop = '''    async def stop(self):
        if self.scheduler:
            logger.info("Stopping automation scheduler")
            self.scheduler.shutdown(wait=False)
            self.scheduler = None
            logger.info("Automation scheduler stopped")
            print("🔥 Automation scheduler stopped", flush=True)'''

new_stop = '''    async def stop(self):
        if self.scheduler:
            logger.info("Stopping automation scheduler")
            self.scheduler.shutdown(wait=False)
            self.scheduler = None
            logger.info("Automation scheduler stopped")
            print("🔥 Automation scheduler stopped", flush=True)

        # Останавливаем AutomationManager v2 если он был запущен
        if USE_AUTOMATION_V2:
            logger.info("Stopping AutomationManager v2...")
            await automation_manager_v2.stop()
            print("🔥 AutomationManager v2 stopped", flush=True)'''

if old_stop in s and 'Stopping AutomationManager v2' not in s:
    s = s.replace(old_stop, new_stop, 1)
    changes.append('patched stop() with v2 manager shutdown')
elif 'Stopping AutomationManager v2' in s:
    changes.append('stop() already patched')

# ФИКС 4: Патчим run_channel_automation() - добавляем выбор manager
old_run = '''        try:
            result = await automation_manager.run_channel(channel_id)'''

new_run = '''        try:
            # Выбираем какой manager использовать на основе feature flag
            if USE_AUTOMATION_V2:
                logger.info("Using AutomationManager v2 for channel %s", channel_id)
                result = await automation_manager_v2.run_channel_now(channel_id)
            else:
                logger.info("Using legacy AutomationManager (v1) for channel %s", channel_id)
                result = await automation_manager.run_channel(channel_id)'''

if old_run in s and 'Using AutomationManager v2 for channel' not in s:
    s = s.replace(old_run, new_run, 1)
    changes.append('patched run_channel_automation() with v2 manager selection')
elif 'Using AutomationManager v2 for channel' in s:
    changes.append('run_channel_automation() already patched')

# Сохраняем
if changes:
    p.write_text(s, encoding='utf-8')
    print(f'✅ Применены фиксы:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Все патчи уже применены')

# ВЕРИФИКАЦИЯ
print('\n=== Проверка после фиксов ===')
new_s = p.read_text(encoding='utf-8')
print(f'logger дубликатов: {new_s.count("logger = logging.getLogger(__name__)")}')
print(f'USE_AUTOMATION_V2 встречается: {new_s.count("USE_AUTOMATION_V2")} раз')
print(f'automation_manager_v2.start() в start(): {"AutomationManager v2 ENABLED" in new_s}')
print(f'automation_manager_v2.stop() в stop(): {"Stopping AutomationManager v2" in new_s}')
print(f'run_channel_now в run_channel_automation(): {"Using AutomationManager v2 for channel" in new_s}')