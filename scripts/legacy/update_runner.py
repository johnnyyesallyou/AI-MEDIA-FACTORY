file_path = '/app/backend/automation/runner.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Обновляем первый вызов job.run(channel=channel)
content = content.replace(
    'job_result = job.run(\n                    channel=channel\n                )',
    'job_result = job.run(\n                    channel=channel,\n                    execution_id=execution_id\n                )'
)

# 2. Обновляем второй вызов job.run() (в блоке except TypeError)
content = content.replace(
    'job_result = job.run()',
    'job_result = job.run(execution_id=execution_id)'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ runner.py успешно обновлен! Теперь execution_id передается во все джобы.')
