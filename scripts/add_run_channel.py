import pathlib
p = pathlib.Path('./backend/automation/manager.py')
s = p.read_text(encoding='utf-8')

# Добавляем метод run_channel перед run_all_channels
new_method = '''
    async def run_channel(self, channel_id: str):
        """Запускает автоматизацию для одного конкретного канала."""
        db = SessionLocal()
        try:
            channel = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
            if not channel:
                logger.warning("Channel %s not found", channel_id)
                return {"status": "failed", "error": "Channel not found"}
            
            if not channel.is_active:
                logger.info("Channel %s is not active, skipping", channel.name)
                return {"status": "skipped", "reason": "Channel not active"}
            
            logger.info("Starting automation for single channel %s", channel.name)
            result = await self.runner.run_now(channel=channel)
            
            return {
                "status": "completed",
                "channel_id": channel.id,
                "channel_name": channel.name,
                "result": result
            }
        finally:
            db.close()

'''

# Вставляем метод перед def run_all_channels
if 'async def run_channel' not in s:
    s = s.replace('    async def run_all_channels(self):', new_method + '    async def run_all_channels(self):')
    p.write_text(s, encoding='utf-8')
    print("✅ Добавлен метод run_channel в AutomationManager")
else:
    print("ℹ️ Метод run_channel уже существует")