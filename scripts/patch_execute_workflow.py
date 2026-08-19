import pathlib
p = pathlib.Path('./backend/automation/automation_manager_v2.py')
s = p.read_text(encoding='utf-8')
old = '''                # Выполняем workflow
                logger.info(f"Executing workflow for channel {task.channel_name}")
                result = await self.runner.run_now(channel=channel)'''
new = '''                # Sprint 8.4: если каналу назначен workflow — выполняем граф из БД
                workflow_id = getattr(channel, "workflow_id", None)
                if workflow_id:
                    logger.info(f"Executing workflow {workflow_id} for channel {task.channel_name}")
                    result = await self.runner.run_now(channel=channel, workflow_id=workflow_id)
                else:
                    logger.info(f"Channel has no workflow_id, using default pipeline for {task.channel_name}")
                    result = await self.runner.run_now(channel=channel)'''
if old in s:
    s = s.replace(old, new, 1)
    p.write_text(s, encoding='utf-8')
    print('OK: _execute_task now respects channel.workflow_id')
else:
    print('WARN: pattern not found — проверь вручную')