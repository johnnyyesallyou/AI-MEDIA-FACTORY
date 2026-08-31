import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.repositories.channel_repository import ChannelRepository
from backend.automation.jobs.automation_jobs import PublishJob

db = SessionLocal()
try:
    repo = ChannelRepository(db)
    channel = repo.get('35a85a18-7a61-4386-9d96-c64fac0fa217')  # AI Anime News
    
    print(f'Канал: {channel.name}')
    print(f'  platform: {channel.platform}')
    print(f'  chat_id: {channel.chat_id}')
    print(f'  is_connected: {channel.is_connected}')
    
    job = PublishJob()
    result = job.run(channel=channel, execution_id='test-image-publish')
    
    print('\\n=== Результат PublishJob ===')
    for key, value in result.items():
        print(f'   {key}: {value}')
finally:
    db.close()