import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8')
changes = []

# ФИКС 1: удаляем импорт несуществующего base_job
old_import = 'from backend.automation.jobs.base_job import BaseJob\n'
if old_import in s:
    s = s.replace(old_import, '', 1)
    changes.append('Removed base_job import')

# ФИКС 2: убираем наследование от BaseJob
old_class = 'class WritingJob(BaseJob):'
new_class = 'class WritingJob:'
if old_class in s:
    s = s.replace(old_class, new_class, 1)
    changes.append('WritingJob no longer inherits from BaseJob')

# ФИКС 3: заменяем self.get_db() на SessionLocal()
old_db = 'db: Session = self.get_db()'
new_db = 'db = SessionLocal()'
if old_db in s:
    s = s.replace(old_db, new_db, 1)
    changes.append('db = SessionLocal() instead of self.get_db()')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы:')
    for c in changes:
        print(f'  - {c}')
else:
    print('WARN: паттерны не найдены')

# ВЕРИФИКАЦИЯ
print('\n=== Проверка ===')
new_s = p.read_text(encoding='utf-8')
print(f'base_job импортируется: {"base_job" in new_s}')
print(f'WritingJob наследуется от BaseJob: {"class WritingJob(BaseJob)" in new_s}')
print(f'self.get_db() в файле: {"self.get_db" in new_s}')