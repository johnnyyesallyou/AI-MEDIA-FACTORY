import pathlib

p = pathlib.Path('./backend/automation/automation_manager_v2.py')
s = p.read_text(encoding='utf-8')
changes = []

# ФИКС: убираем execution_id из вызова run_now()
old_call = '''                result = await self.runner.run_now(
                    channel=channel,
                    execution_id=task.execution_id
                )'''

new_call = '''                result = await self.runner.run_now(channel=channel)'''

if old_call in s:
    s = s.replace(old_call, new_call, 1)
    changes.append('removed execution_id from run_now() call')
else:
    print('WARN: pattern not found')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Ничего не изменилось')