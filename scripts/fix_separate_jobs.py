import re

files_to_fix = [
    '/app/backend/automation/jobs/revision_job.py',
    '/app/backend/automation/jobs/re_evaluation_job.py'
]

for file_path in files_to_fix:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавляем execution_id в сигнатуру метода run
        # Поддерживает как def run(self, channel=None), так и async def run
        content = re.sub(
            r'(def run\(self, channel=None)(\) -> dict\[str, Any\]:)',
            r'\1, execution_id: str = None\2',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ {file_path.split('/')[-1]} успешно обновлен!")
    except FileNotFoundError:
        print(f"⚠️ Файл {file_path} не найден")
