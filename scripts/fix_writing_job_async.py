import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8')

# Меняем def run на async def run в классе WritingJob
old_sig = 'class WritingJob(BaseJob):\n    """Р"РµРЅРµРЅРµСЂРёСЂСѓРµС‚ РєРѕРЅС‚РµРЅС‚ РёР· research items."""\n\n    def run(self, channel: Any = None, execution_id: str = None) -> Dict[str, Any]:'

new_sig = 'class WritingJob(BaseJob):\n    """Р"РµРЅРµРЅРµСЂРёСЂСѓРµС‚ РєРѕРЅС‚РµРЅС‚ РёР· research items."""\n\n    async def run(self, channel: Any = None, execution_id: str = None) -> Dict[str, Any]:'

if old_sig in s:
    s = s.replace(old_sig, new_sig)
    p.write_text(s, encoding='utf-8')
    print('OK: WritingJob.run() теперь async (может использовать await)')
else:
    print('WARN: паттерн не найден')