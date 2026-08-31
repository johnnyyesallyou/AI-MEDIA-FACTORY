import sys, asyncio, traceback
sys.path.insert(0, '/app')

log_file = open('/tmp/publish_result.txt', 'w', encoding='utf-8')

def log(msg):
    print(msg)
    log_file.write(str(msg) + '\n')
    log_file.flush()

async def run_publish():
    try:
        log('=== Импорт зависимостей ===')
        from core.database import SessionLocal
        from core.repositories.channel_repository import ChannelRepository
        from backend.automation.jobs.automation_jobs import PublishJob
        log('✅ Импорты успешны')
        
        log('\\n=== Получаем VK канал ===')
        db = SessionLocal()
        repo = ChannelRepository(db)
        channel = repo.get('4400626c-e53d-46fa-a49a-65791cb2948a')
        db.close()
        
        if not channel:
            log('❌ Канал не найден')
            return
        
        log(f'✅ Канал: {channel.name}')
        log(f'   platform: {channel.platform}')
        log(f'   vk_group_id: {channel.vk_group_id}')
        log(f'   is_connected: {channel.is_connected}')
        
        log('\\n=== Запускаем PublishJob ===')
        job = PublishJob()
        result = await job.run(channel=channel, execution_id='manual-publish-001')
        
        log('\\n=== Результат PublishJob ===')
        for key, value in result.items():
            log(f'   {key}: {value}')
        
    except Exception as e:
        log(f'\\n❌ ОШИБКА: {type(e).__name__}: {e}')
        log(traceback.format_exc())

try:
    asyncio.run(run_publish())
except Exception as e:
    print(f'Critical: {e}')