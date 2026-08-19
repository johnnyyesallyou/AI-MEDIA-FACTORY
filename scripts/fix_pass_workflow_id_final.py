import pathlib, re
p = pathlib.Path('./backend/automation/automation_manager_v2.py')
s = p.read_text(encoding='utf-8')
changes = []

# Ищем вызов runner.run_now и добавляем workflow_id из канала
# Шаблон: "result = await self.runner.run_now(channel=channel)"
old_call = r'(result = await self\.runner\.run_now\(channel=channel\))'
new_call = r'''# Sprint 8.4.1: передаём workflow_id из канала в runner
                workflow_id = getattr(channel, "workflow_id", None)
                if workflow_id:
                    logger.info(f"Executing workflow {workflow_id} from channel for {task.channel_name}")
                    result = await self.runner.run_now(channel=channel, workflow_id=workflow_id)
                else:
                    logger.info(f"Channel has no workflow_id, using default pipeline for {task.channel_name}")
                    result = await self.runner.run_now(channel=channel)'''

s_new, count = re.subn(old_call, new_call, s, count=1)
if count > 0 and 'Executing workflow' not in s:
    s = s_new
    changes.append('added workflow_id parameter to runner.run_now() call')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы:')
    for c in changes:
        print(f'   ✅ {c}')
else:
    print('ℹ️ Ничего не изменилось (патч уже применён или паттерн не найден)')