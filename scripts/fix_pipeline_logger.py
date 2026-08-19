import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8')

# Удаляем строку 195 (фантомный импорт)
old_line = 'from backend.automation.pipeline_logger import PipelineLogger\n'
if old_line in s:
    s = s.replace(old_line, '', 1)
    p.write_text(s, encoding='utf-8')
    print('OK: удалён фантомный импорт pipeline_logger')
    print('    (PipelineLogger определён в том же файле на строке 34)')
else:
    print('WARN: строка не найдена')

# ВЕРИФИКАЦИЯ
print('\n=== Проверка ===')
new_s = p.read_text(encoding='utf-8')
print(f'pipeline_logger импортируется: {"pipeline_logger" in new_s}')
print(f'class PipelineLogger в файле: {"class PipelineLogger" in new_s}')