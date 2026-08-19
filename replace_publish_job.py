import pathlib, py_compile, re

f = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = f.read_text(encoding='utf-8')

# Читаем новый PublishJob
new_code = pathlib.Path('./new_publish_job.py').read_text(encoding='utf-8')

# Ищем начало и конец старого PublishJob
# Начало: "class PublishJob:"
# Конец: следующая строка с "class " на уровне отступа 0 или конец файла

lines = s.split('\n')
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if line.startswith('class PublishJob:'):
        start_idx = i
    elif start_idx is not None and line.startswith('class ') and i > start_idx:
        end_idx = i
        break

if start_idx is not None:
    if end_idx is None:
        end_idx = len(lines)
    
    print(f"Старый PublishJob: строки {start_idx+1}-{end_idx}")
    
    # Заменяем
    new_lines = lines[:start_idx] + new_code.split('\n') + lines[end_idx:]
    f.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"✅ PublishJob заменён (новый: {len(new_code.split(chr(10)))} строк)")
else:
    print("❌ PublishJob не найден")

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ automation_jobs.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")