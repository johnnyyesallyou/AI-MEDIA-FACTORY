import re

file_path = './backend/automation/jobs/automation_jobs.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Добавляем p_logger.finish перед return в WritingJob
# Ищем блок return со статусом ok и items_processed, независимо от пробелов
pattern_writing = r'(\s+)return \{\s+"status": "ok",\s+"items_processed": processed,\s+"failed": failed\s+\}'
replacement_writing = r'''\1p_logger.finish("success", details=f"Processed {processed}, failed {failed}")
\1return {
\1    "status": "ok",
\1    "items_processed": processed,
\1    "failed": failed
\1}'''
content = re.sub(pattern_writing, replacement_writing, content)

# 2. Добавляем p_logger.finish перед return в EvaluatorJob
pattern_eval = r'(\s+)return \{\s+"status": "ok",\s+"processed": processed,\s+"approved": approved\s+\}'
replacement_eval = r'''\1p_logger.finish("success", details=f"Processed {processed}, approved {approved}")
\1return {
\1    "status": "ok",
\1    "processed": processed,
\1    "approved": approved
\1}'''
content = re.sub(pattern_eval, replacement_eval, content)

# 3. Добавляем p_logger.finish в блок except WritingJob (если он там есть и там нет finish)
if 'class WritingJob:' in content and 'p_logger.finish("failed"' not in content.split('class EvaluatorJob:')[0]:
    content = re.sub(
        r'(except Exception as e:\s+failed \+= 1\s+db\.rollback\(\)\s+logger\.exception\(\s+"Writing failed item=%s error=%s",\s+item\.id,\s+e\s+\))',
        r'\1\n            p_logger.finish("failed", error_message=str(e))',
        content
    )

# 4. Добавляем p_logger.finish в блок except EvaluatorJob (если он там есть)
if 'class EvaluatorJob:' in content and 'p_logger.finish("failed"' not in content.split('class RevisionJob:')[0]:
    content = re.sub(
        r'(except Exception as e:\s+db\.rollback\(\)\s+logger\.exception\(\s+"Evaluation failed.*?\))',
        r'\1\n            p_logger.finish("failed", error_message=str(e))',
        content,
        flags=re.DOTALL
    )

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ automation_jobs.py успешно пропатчен!")
