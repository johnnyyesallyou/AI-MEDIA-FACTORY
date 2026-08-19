import pathlib

p = pathlib.Path('./backend/automation/automation_manager_v2.py')
s = p.read_text(encoding='utf-8')
changes = []

# ФИКС 1: Добавляем print в _load_channels
old_load = '''    async def _load_channels(self):
        """Р—Р°РіСЂСѓР¶Р°РµС‚ РІСЃРµ Р°РєС‚РёРІРЅС‹Рµ РєР°РЅР°Р»С‹ РёР· Р‘Р”."""
        db = SessionLocal()
        try:
            channels = db.query(ChannelORM).filter(ChannelORM.is_active == True).all()
            for channel in channels:
                self.channels[channel.id] = channel
                logger.info(f"Loaded channel: {channel.name} (id={channel.id})")
        finally:
            db.close()'''

new_load = '''    async def _load_channels(self):
        """Р—Р°РіСЂСѓР¶Р°РµС‚ РІСЃРµ Р°РєС‚РёРІРЅС‹Рµ РєР°РЅР°Р»С‹ РёР· Р‘Р”."""
        print("🔍 Loading channels from DB...", flush=True)
        db = SessionLocal()
        try:
            channels = db.query(ChannelORM).filter(ChannelORM.is_active == True).all()
            print(f"📊 Found {len(channels)} active channels", flush=True)
            for channel in channels:
                self.channels[channel.id] = channel
                logger.info(f"Loaded channel: {channel.name} (id={channel.id})")
                print(f"  ✅ Loaded: {channel.name} ({channel.id})", flush=True)
        finally:
            db.close()'''

if old_load in s:
    s = s.replace(old_load, new_load, 1)
    changes.append('added print to _load_channels')

# ФИКС 2: Добавляем print в _create_channel_queue
old_queue = '''    async def _create_channel_queue(self, channel_id: str):
        """РЎРѕР·РґР°С‘С‚ РёР·РѕР»РёСЂРѕРІР°РЅРЅСѓСЋ РѕС‡РµСЂРµРґСЊ РґР»СЏ РєР°РЅР°Р»Р°."""
        if channel_id not in self.channel_queues:
            self.channel_queues[channel_id] = asyncio.Queue()
            logger.info(f"Created queue for channel {channel_id}")'''

new_queue = '''    async def _create_channel_queue(self, channel_id: str):
        """РЎРѕР·РґР°С‘С‚ РёР·РѕР»РёСЂРѕРІР°РЅРЅСѓСЋ РѕС‡РµСЂРµРґСЊ РґР»СЏ РєР°РЅР°Р»Р°."""
        if channel_id not in self.channel_queues:
            self.channel_queues[channel_id] = asyncio.Queue()
            logger.info(f"Created queue for channel {channel_id}")
            print(f"  📦 Created queue for {channel_id[:8]}...", flush=True)'''

if old_queue in s:
    s = s.replace(old_queue, new_queue, 1)
    changes.append('added print to _create_channel_queue')

# ФИКС 3: Добавляем print в _start_channel_worker
old_worker = '''    async def _start_channel_worker(self, channel_id: str):
        """Р—Р°РїСѓСЃРєР°РµС‚ worker РґР»СЏ РѕР±СЂР°Р±РѕС‚РєРё РѕС‡РµСЂРµРґРё РєР°РЅР°Р»Р°."""
        if channel_id not in self.workers:
            worker_task = asyncio.create_task(self._channel_worker(channel_id))
            self.workers[channel_id] = worker_task
            logger.info(f"Started worker for channel {channel_id}")'''

new_worker = '''    async def _start_channel_worker(self, channel_id: str):
        """Р—Р°РїСѓСЃРєР°РµС‚ worker РґР»СЏ РѕР±СЂР°Р±РѕС‚РєРё РѕС‡РµСЂРµРґРё РєР°РЅР°Р»Р°."""
        if channel_id not in self.workers:
            print(f"  🚀 Starting worker for {channel_id[:8]}...", flush=True)
            worker_task = asyncio.create_task(self._channel_worker(channel_id))
            self.workers[channel_id] = worker_task
            logger.info(f"Started worker for channel {channel_id}")
            print(f"  ✅ Worker started for {channel_id[:8]}...", flush=True)'''

if old_worker in s:
    s = s.replace(old_worker, new_worker, 1)
    changes.append('added print to _start_channel_worker')

# ФИКС 4: Добавляем print в _enqueue_task
old_enqueue = '''    async def _enqueue_task(self, task: ChannelTask):
        """Р”РѕР±Р°РІР»СЏРµС‚ Р·Р°РґР°С‡Сѓ РІ РѕС‡РµСЂРµРґСЊ РєР°РЅР°Р»Р°."""
        if task.channel_id in self.channel_queues:
            await self.channel_queues[task.channel_id].put(task)
            logger.info(f"Enqueued task {task.task_id} for channel {task.channel_name}")
        else:
            logger.error(f"Queue not found for channel {task.channel_id}")'''

new_enqueue = '''    async def _enqueue_task(self, task: ChannelTask):
        """Р”РѕР±Р°РІР»СЏРµС‚ Р·Р°РґР°С‡Сѓ РІ РѕС‡РµСЂРµРґСЊ РєР°РЅР°Р»Р°."""
        if task.channel_id in self.channel_queues:
            await self.channel_queues[task.channel_id].put(task)
            logger.info(f"Enqueued task {task.task_id} for channel {task.channel_name}")
            print(f"📥 Enqueued task {task.task_id[:8]}... for {task.channel_name}", flush=True)
            print(f"   Queue size now: {self.channel_queues[task.channel_id].qsize()}", flush=True)
        else:
            logger.error(f"Queue not found for channel {task.channel_id}")
            print(f"❌ Queue NOT found for {task.channel_id}", flush=True)'''

if old_enqueue in s:
    s = s.replace(old_enqueue, new_enqueue, 1)
    changes.append('added print to _enqueue_task')

# ФИКС 5: Добавляем print в _channel_worker
old_channel_worker = '''    async def _channel_worker(self, channel_id: str):
        """Worker РґР»СЏ РѕР±СЂР°Р±РѕС‚РєРё Р·Р°РґР°С‡ РёР· РѕС‡РµСЂРµРґРё РєР°РЅР°Р»Р°."""
        logger.info(f"Channel worker started for {channel_id}")

        while True:
            try:
                task: ChannelTask = await self.channel_queues[channel_id].get()

                logger.info(f"Processing task {task.task_id} for channel {task.channel_name}")

                await self._execute_task(task)

                self.channel_queues[channel_id].task_done()'''

new_channel_worker = '''    async def _channel_worker(self, channel_id: str):
        """Worker РґР»СЏ РѕР±СЂР°Р±РѕС‚РєРё Р·Р°РґР°С‡ РёР· РѕС‡РµСЂРµРґРё РєР°РЅР°Р»Р°."""
        logger.info(f"Channel worker started for {channel_id}")
        print(f"⚡ Channel worker ACTIVE for {channel_id[:8]}... waiting for tasks", flush=True)

        while True:
            try:
                print(f"   ⏳ Waiting for task in queue {channel_id[:8]}...", flush=True)
                task: ChannelTask = await self.channel_queues[channel_id].get()
                print(f"   📤 Got task {task.task_id[:8]}... from queue", flush=True)

                logger.info(f"Processing task {task.task_id} for channel {task.channel_name}")
                print(f"   🔨 Processing task {task.task_id[:8]}... for {task.channel_name}", flush=True)

                await self._execute_task(task)

                self.channel_queues[channel_id].task_done()
                print(f"   ✅ Task {task.task_id[:8]}... done", flush=True)'''

if old_channel_worker in s:
    s = s.replace(old_channel_worker, new_channel_worker, 1)
    changes.append('added print to _channel_worker')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Ничего не изменилось')