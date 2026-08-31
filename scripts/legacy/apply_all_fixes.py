import re

# --- 1. Исправляем automation_jobs.py ---
jobs_file = '/app/backend/automation/jobs/automation_jobs.py'
with open(jobs_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Добавляем execution_id во ВСЕ методы run(self, channel=None)
content = re.sub(
    r'(def run\(self, channel=None)(\) -> dict\[str, Any\]:)',
    r'\1, execution_id: str = None\2',
    content
)

# Добавляем логгер в RevisionJob, если его там нет
if 'class RevisionJob:' in content and 'p_logger.start("revision")' not in content:
    content = re.sub(
        r'(class RevisionJob:\s+def run\(self, channel=None, execution_id: str = None\) -> dict\[str, Any\]:)',
        r'\1\n        p_logger = PipelineLogger(execution_id, channel.id if channel else None)\n        p_logger.start("revision")',
        content
    )

# Добавляем логгер в ReEvaluationJob, если его там нет
if 'class ReEvaluationJob:' in content and 'p_logger.start("re_evaluation")' not in content:
    content = re.sub(
        r'(class ReEvaluationJob:\s+def run\(self, channel=None, execution_id: str = None\) -> dict\[str, Any\]:)',
        r'\1\n        p_logger = PipelineLogger(execution_id, channel.id if channel else None)\n        p_logger.start("re_evaluation")',
        content
    )

with open(jobs_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ automation_jobs.py успешно обновлен!")

# --- 2. Исправляем runner.py (удаляем вредный блок except TypeError) ---
runner_file = '/app/backend/automation/runner.py'
with open(runner_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_block = False

for line in lines:
    if 'except TypeError:' in line:
        skip_block = True
        continue
    
    if skip_block:
        # Прерываем пропуск, когда встречаем строку с меньшим отступом (конец блока except)
        if line.strip() and not line.startswith('                ') and not line.startswith('\t\t\t\t'):
            skip_block = False
            new_lines.append(line)
        continue
        
    new_lines.append(line)

with open(runner_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ runner.py успешно обновлен (вредный блок удален)!")
