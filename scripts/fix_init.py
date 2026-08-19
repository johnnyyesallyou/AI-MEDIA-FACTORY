import pathlib

# Проверяем какие классы есть в automation_jobs.py
f = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = f.read_text(encoding='utf-8')

available_classes = []
for class_name in ['ResearchJob', 'DecisionJob', 'WritingJob', 'EvaluatorJob', 'PublishJob', 'RevisionJob', 'ReEvaluationJob']:
    if f'class {class_name}' in s:
        available_classes.append(class_name)
        print(f'  ✅ {class_name} найден')
    else:
        print(f'  ❌ {class_name} НЕ найден')

# Проверяем есть ли ImageJob
image_job_exists = pathlib.Path('./backend/automation/jobs/image_job.py').exists()
if image_job_exists:
    print('  ✅ ImageJob найден')
else:
    print('  ❌ ImageJob НЕ найден')

# Генерируем __init__.py
init_lines = ['from .automation_jobs import (']
for cls in available_classes:
    init_lines.append(f'    {cls},')
init_lines.append(')')

if image_job_exists:
    init_lines.append('from .image_job import ImageJob')

init_lines.append('')
init_lines.append('__all__ = [')
for cls in available_classes:
    init_lines.append(f'    "{cls}",')
if image_job_exists:
    init_lines.append('    "ImageJob",')
init_lines.append(']')

init_content = '\n'.join(init_lines)
f_init = pathlib.Path('./backend/automation/jobs/__init__.py')
f_init.write_text(init_content, encoding='utf-8')

print(f'\\n✅ __init__.py обновлён с {len(available_classes)} классами')
print('\\nСодержимое:')
print(init_content)

import py_compile
try:
    py_compile.compile(str(f_init), doraise=True)
    print('\\n✅✅✅ __init__.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'\\n❌ Ошибка: {e}')