import re

file_path = '/app/backend/automation/jobs/automation_jobs.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Функция для безопасного добавления execution_id в сигнатуру метода run
def add_exec_id_to_job(content, job_name):
    # Ищем "class JobName:" затем пробелы/переносы, затем "def run(self, channel=None)"
    pattern = rf"(class {job_name}:\s+def run\(self, channel=None)(\) -> dict\[str, Any\]:)"
    replacement = r"\1, execution_id: str = None\2"
    return re.sub(pattern, replacement, content)

# Обновляем пропущенные джобы
content = add_exec_id_to_job(content, "DecisionJob")
content = add_exec_id_to_job(content, "RevisionJob")
content = add_exec_id_to_job(content, "ReEvaluationJob")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ DecisionJob, RevisionJob и ReEvaluationJob успешно обновлены!')
