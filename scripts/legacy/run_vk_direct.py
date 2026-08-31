import sys, asyncio
sys.path.insert(0, '/app')

from core.database import SessionLocal
from core.repositories.channel_repository import ChannelRepository
from backend.automation.runner import AutomationRunner

async def run_vk_channel():
    db = SessionLocal()
    try:
        repo = ChannelRepository(db)
        channel = repo.get('4400626c-e53d-46fa-a49a-65791cb2948a')
        if not channel:
            print('❌ Канал не найден в БД')
            return
        
        print(f'✅ Канал найден: {channel.name}')
        print(f'   platform: {channel.platform}')
        print(f'   workflow_id: {channel.workflow_id}')
        print(f'   vk_group_id: {channel.vk_group_id}')
        
        runner = AutomationRunner()
        result = await runner.run_now(
            channel=channel,
            workflow_id=channel.workflow_id
        )
        
        print(f'\\n🎯 Result:')
        print(f'   execution_id: {result.get("execution_id")}')
        print(f'   status: {result.get("status")}')
        print(f'   workflow_id: {result.get("workflow_id")}')
    finally:
        db.close()

asyncio.run(run_vk_channel())