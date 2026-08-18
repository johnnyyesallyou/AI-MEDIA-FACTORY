import pathlib
import re

p = pathlib.Path('./backend/automation/automation_manager_v2.py')
s = p.read_text(encoding='utf-8')
changes = []

# ФИКС 1: Добавляем print в _load_channels (regex)
old_pattern = r'(async def _load_channels\(self\):\s+"""[^"]*""")'
new_text = r'''\1
        print("🔍 Loading channels from DB...", flush=True)'''
if not '🔍 Loading channels' in s:
    s_new, count = re.subn(old_pattern, new_text, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added debug print to _load_channels start')

# ФИКС 2: Логируем после self.channels[channel.id] = channel
old_pattern2 = r'(self\.channels\[channel\.id\] = channel\s+logger\.info\(f"Loaded channel: \{channel\.name\})'
new_text2 = r'''print(f"  ✅ Loaded channel: {channel.name} ({channel.id})", flush=True)
                \1'''
if not '✅ Loaded channel' in s:
    s_new, count = re.subn(old_pattern2, new_text2, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added debug print after channel load')

# ФИКС 3: Логируем в _create_channel_queue
old_pattern3 = r'(self\.channel_queues\[channel_id\] = asyncio\.Queue\(\)\s+logger\.info\(f"Created queue for channel \{channel_id\}"\))'
new_text3 = r'''\1
            print(f"  📦 Created queue for {channel_id[:8]}...", flush=True)'''
if not '📦 Created queue' in s:
    s_new, count = re.subn(old_pattern3, new_text3, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added debug print to _create_channel_queue')

# ФИКС 4: Логируем в _start_channel_worker
old_pattern4 = r'(worker_task = asyncio\.create_task\(self\._channel_worker\(channel_id\)\)\s+self\.workers\[channel_id\] = worker_task\s+logger\.info\(f"Started worker for channel \{channel_id\}"\))'
new_text4 = r'''print(f"  🚀 Creating asyncio task for {channel_id[:8]}...", flush=True)
            \1
            print(f"  ✅ Worker task created for {channel_id[:8]}...", flush=True)'''
if not '🚀 Creating asyncio task' in s:
    s_new, count = re.subn(old_pattern4, new_text4, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added debug print to _start_channel_worker')

# ФИКС 5: Логируем в _channel_worker (самое важное)
old_pattern5 = r'(async def _channel_worker\(self, channel_id: str\):\s+"""[^"]*"""\s+logger\.info\(f"Channel worker started for \{channel_id\}"\))'
new_text5 = r'''\1
        print(f"⚡⚡⚡ CHANNEL WORKER ACTIVE for {channel_id} ⚡⚡⚡", flush=True)
        print(f"   Queue object: {self.channel_queues.get(channel_id)}", flush=True)'''
if not '⚡⚡⚡ CHANNEL WORKER ACTIVE' in s:
    s_new, count = re.subn(old_pattern5, new_text5, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added debug print to _channel_worker start')

# ФИКС 6: Логируем когда задача забрана из очереди
old_pattern6 = r'(task: ChannelTask = await self\.channel_queues\[channel_id\]\.get\(\))'
new_text6 = r'''print(f"   ⏳ Waiting for task in queue {channel_id[:8]}...", flush=True)
                \1
                print(f"   📤 GOT TASK! {task.task_id} for {task.channel_name}", flush=True)'''
if not '📤 GOT TASK' in s:
    s_new, count = re.subn(old_pattern6, new_text6, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added debug print around queue.get()')

# ФИКС 7: Логируем _enqueue_task
old_pattern7 = r'(await self\.channel_queues\[task\.channel_id\]\.put\(task\)\s+logger\.info\(f"Enqueued task \{task\.task_id\})'
new_text7 = r'''print(f"📥 ENQUEUING task {task.task_id} into queue {task.channel_id[:8]}", flush=True)
            print(f"   Queue exists: {task.channel_id in self.channel_queues}", flush=True)
            print(f"   Queue size before: {self.channel_queues[task.channel_id].qsize()}", flush=True)
            \1'''
if not '📥 ENQUEUING task' in s:
    s_new, count = re.subn(old_pattern7, new_text7, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added debug print to _enqueue_task')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применено {len(changes)} фиксов:')
    for c in changes:
        print(f'   ✅ {c}')
else:
    print('ℹ️ Ничего не изменилось')