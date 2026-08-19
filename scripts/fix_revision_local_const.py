import pathlib

p = pathlib.Path('./backend/automation/jobs/revision_job.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')

# Ищем строку "def run" и добавляем константу ПЕРЕД ней
old_def = '''    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("revision")

        logger.info("=== REVISION JOB STARTED ===")'''

new_def = '''    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        MAX_REVISION_COUNT = 3  # Локальная константа для защиты от бесконечного цикла
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("revision")

        logger.info("=== REVISION JOB STARTED ===")'''

if old_def in s:
    s = s.replace(old_def, new_def)
    # Также заменяем self.MAX_REVISION_COUNT на просто MAX_REVISION_COUNT
    s = s.replace('self.MAX_REVISION_COUNT', 'MAX_REVISION_COUNT')
    p.write_text(s, encoding='utf-8')
    print('OK: MAX_REVISION_COUNT добавлен как локальная переменная в run()')
else:
    print('ERROR: паттерн не найден')