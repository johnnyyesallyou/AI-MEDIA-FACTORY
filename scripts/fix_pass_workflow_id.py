import pathlib
p = pathlib.Path('./backend/automation/automation_manager_v2.py')
s = p.read_text(encoding='utf-8')
changes = []

# Ищем вызов runner.run_now и добавляем workflow_id из канала
old_call = '''                result = await self.runner.run_now(channel=channel)'''
new_call = '''                # Sprint 8.4.1: передаём workflow_id из канала в runner
                workflow_id = getattr(channel, "workflow_id", None)
                if workflow_id:
                    logger.info(f"Executing workflow {workflow_id} for channel {task.channel_name}")
                    result = await self.runner.run_now(channel=channel, workflow_id=workflow_id)
                else:
                    logger.info(f"Channel has no workflow_id, using default pipeline")
                    result = await self.runner.run_now(channel=channel)'''

if old_call in s and 'Executing workflow' not in s:
    s = s.replace(old_call, new_call, 1)
    changes.append('added workflow_id parameter to runner.run_now() call')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы:')
    for c in changes:
        print(f'   ✅ {c}')
else:
    print('ℹ️ Ничего не изменилось')