import sys, traceback
sys.path.insert(0, '/app')

log_file = open('/tmp/publish_result2.txt', 'w', encoding='utf-8')

def log(msg):
    print(msg)
    log_file.write(str(msg) + '\n')
    log_file.flush()

def run_publish():
    try:
        log('=== Импорт зависимостей ===')
        from core.database import SessionLocal
        from core.repositories.channel_repository import ChannelRepository
        from backend.automation.jobs.automation_jobs import PublishJob
        log('OK Imports successful')
        
        log('\\n=== Get VK channel ===')
        db = SessionLocal()
        repo = ChannelRepository(db)
        channel = repo.get('4400626c-e53d-46fa-a49a-65791cb2948a')
        db.close()
        
        if not channel:
            log('Channel not found')
            return
        
        log(f'Channel: {channel.name}')
        log(f'   platform: {channel.platform}')
        log(f'   vk_group_id: {channel.vk_group_id}')
        log(f'   vk_access_token: {channel.vk_access_token[:20] if channel.vk_access_token else None}...')
        log(f'   bot_token: {channel.bot_token}')
        log(f'   chat_id: {channel.chat_id}')
        
        log('\\n=== Run PublishJob (sync) ===')
        job = PublishJob()
        # Убираем await — PublishJob.run() синхронный
        result = job.run(channel=channel, execution_id='manual-publish-002')
        
        log('\\n=== Result ===')
        for key, value in result.items():
            log(f'   {key}: {value}')
        
    except Exception as e:
        log(f'\\nERROR: {type(e).__name__}: {e}')
        log(traceback.format_exc())
    finally:
        log_file.close()

run_publish()