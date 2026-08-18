import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8')

# Заменяем repo.list на repo.list_all в WritingJob
old_call = 'items = repo.list(status="research", limit=50)'
new_call = 'items = repo.list_all(status="research", limit=50)'

if old_call in s:
    s = s.replace(old_call, new_call, 1)
    p.write_text(s, encoding='utf-8')
    print('OK: repo.list заменён на repo.list_all')
else:
    print('WARN: паттерн не найден')