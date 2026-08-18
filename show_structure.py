import pathlib, py_compile, re

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

# Нам нужно понять структуру блока for item in items:
# Ищем "for item in items:" в PublishJob
publish_job_start = None
for i, line in enumerate(lines):
    if 'class PublishJob' in line:
        publish_job_start = i
        break

if not publish_job_start:
    print("❌ PublishJob не найден")
    exit(1)

print(f"PublishJob начинается на строке {publish_job_start + 1}")

# Ищем цикл "for item in items:" внутри PublishJob
for_item_line = None
for i in range(publish_job_start, min(publish_job_start + 200, len(lines))):
    if 'for item in items' in lines[i] or 'for debug_item in items' in lines[i]:
        for_item_line = i
        print(f"Цикл for item найден на строке {i+1}")
        break

# Показываем структуру try/except/for в PublishJob
print("\n📋 Структура PublishJob (for/try/except):")
for i in range(for_item_line or 450, min(len(lines), (for_item_line or 450) + 60)):
    line = lines[i]
    indent = len(line) - len(line.lstrip())
    stripped = line.strip()
    if stripped and (stripped.startswith(('for ', 'if ', 'try:', 'except', 'else:', 'finally:', 'continue', 'break', 'return', 'class ', 'def ')) or 'result = ' in stripped or 'publisher = ' in stripped or 'platform = ' in stripped):
        print(f"   {i+1:4d} [{indent:2}] {stripped[:70]}")