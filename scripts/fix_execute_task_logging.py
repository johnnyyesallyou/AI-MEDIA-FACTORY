import pathlib
import re

p = pathlib.Path('./backend/automation/automation_manager_v2.py')
s = p.read_text(encoding='utf-8')
changes = []

# Логируем начало _execute_task
old_pattern = r'(async def _execute_task\(self, task: ChannelTask\):\s+"""[^"]*""")'
new_text = r'''\1
        print(f"🔨🔨🔨 EXECUTE_TASK START for {task.task_id} ({task.channel_name})", flush=True)'''
if '🔨🔨🔨 EXECUTE_TASK START' not in s:
    s_new, count = re.subn(old_pattern, new_text, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added log at _execute_task start')

# Логируем перед runner.run_now
old_pattern2 = r'(result = await self\.runner\.run_now\(channel=channel\))'
new_text2 = r'''print(f"   🚀 Calling runner.run_now() for {task.task_id}", flush=True)
                \1
                print(f"   ✅ runner.run_now() returned: {result.get('status', 'unknown')}", flush=True)'''
if '🚀 Calling runner.run_now()' not in s:
    s_new, count = re.subn(old_pattern2, new_text2, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added log around runner.run_now()')

# Логируем конец _execute_task
old_pattern3 = r'(self\.channel_queues\[channel_id\]\.task_done\(\)\s+print\(f"   ✅ Task \{task\.task_id\[:8\]\}\.\.\. done", flush=True\))'
new_text3 = r'''\1
                print(f"🎉🎉🎉 TASK COMPLETED: {task.task_id}", flush=True)'''
if '🎉🎉🎉 TASK COMPLETED' not in s:
    s_new, count = re.subn(old_pattern3, new_text3, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added log at _execute_task end')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применено {len(changes)} фиксов:')
    for c in changes:
        print(f'   ✅ {c}')
else:
    print('ℹ️ Ничего не изменилось')