import pathlib
import re
p = pathlib.Path('./backend/automation/automation_manager_v2.py')
s = p.read_text(encoding='utf-8')

# Ищем ЛЮБОЙ вызов self.runner.run_now(channel=channel) БЕЗ workflow_id
# и заменяем на версию с workflow_id из channel
pattern = r'result = await self\.runner\.run_now\(channel=channel\)'
new_code = '''# Sprint 8.4: передаём workflow_id из канала в runner
                workflow_id = getattr(channel, "workflow_id", None)
                if workflow_id:
                    logger.info(f"Executing workflow {workflow_id} from channel for {task.channel_name}")
                    result = await self.runner.run_now(channel=channel, workflow_id=workflow_id)
                else:
                    logger.info(f"Channel has no workflow_id, using default pipeline for {task.channel_name}")
                    result = await self.runner.run_now(channel=channel)'''

matches = re.findall(pattern, s)
print(f"Найдено {len(matches)} вызовов runner.run_now(channel=channel)")

if matches:
    s = re.sub(pattern, new_code, s)
    p.write_text(s, encoding='utf-8')
    print(f"✅ Пропатчено {len(matches)} вызовов")
else:
    print("ℹ️ Паттерн не найден (возможно уже пропатчено)")