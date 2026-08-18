file_path = './backend/automation/jobs/automation_jobs.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Добавляем finish в WritingJob
content = content.replace(
    '            return {\n\n                "status": "ok",\n\n                "items_processed": processed,\n\n                "failed": failed\n\n            }',
    '            p_logger.finish("success", details=f"Processed {processed}, failed {failed}")\n\n            return {\n                "status": "ok",\n                "items_processed": processed,\n                "failed": failed\n            }'
)

# 2. Добавляем finish в EvaluatorJob
content = content.replace(
    '            return {\n\n                "status": "ok",\n\n                "processed": processed,\n\n                "approved": approved\n\n            }',
    '            p_logger.finish("success", details=f"Processed {processed}, approved {approved}")\n\n            return {\n                "status": "ok",\n                "processed": processed,\n                "approved": approved\n            }'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ automation_jobs.py успешно дополнен!")
