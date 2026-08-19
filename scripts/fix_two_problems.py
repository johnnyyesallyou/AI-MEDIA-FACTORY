import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8')
changes = []

# ФИКС 1: делаем WritingJob.run() async (только эту функцию, сигнатура уникальна)
old_sig = '    def run(self, channel: Any = None, execution_id: str = None) -> Dict[str, Any]:'
new_sig = '    async def run(self, channel: Any = None, execution_id: str = None) -> Dict[str, Any]:'
if old_sig in s:
    s = s.replace(old_sig, new_sig, 1)  # только первое вхождение (WritingJob)
    changes.append('WritingJob.run() -> async def run()')

# ФИКС 2: разделяем прилипший return и class EvaluatorJob
old_glue = 'return {"status": "ok", "items_processed": processed, "failed": failed}class EvaluatorJob:'
new_glue = 'return {"status": "ok", "items_processed": processed, "failed": failed}\n\n\nclass EvaluatorJob:'
if old_glue in s:
    s = s.replace(old_glue, new_glue, 1)
    changes.append('Separated return from class EvaluatorJob')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы: {"; ".join(changes)}')
else:
    print('WARN: паттерны не найдены — возможно уже исправлено')

# ВЕРИФИКАЦИЯ
print('\n=== Проверка после фикса ===')
new_s = p.read_text(encoding='utf-8')
print(f'async def run in file: {"async def run(self, channel: Any = None" in new_s}')
print(f'Прилипший return: {"failed}class EvaluatorJob" in new_s}')
print(f'await в WritingJob: {"await writer.generate" in new_s}')