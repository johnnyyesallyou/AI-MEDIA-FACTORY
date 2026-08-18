import sys
import asyncio
sys.path.insert(0, '.')

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.workflow_orm import WorkflowORM
from backend.automation.runner import AutomationRunner

async def test_workflow():
    print("=" * 80)
    print("Тест: run_now() с workflow_id")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # Получаем канал
        channel = db.query(ChannelORM).filter(ChannelORM.is_active == True).first()
        if not channel:
            print("❌ Нет активных каналов")
            return
        
        print(f"\n1. Канал: {channel.name} (id={channel.id})")
        
        # Получаем workflow "Simple"
        workflow = db.query(WorkflowORM).filter(WorkflowORM.name == "Simple").first()
        if not workflow:
            print("❌ Workflow 'Simple' не найден")
            return
        
        print(f"2. Workflow: {workflow.name} (id={workflow.id})")
        
        # Создаём runner
        runner = AutomationRunner()
        
        # Запускаем с workflow_id
        print(f"\n3. Запуск run_now(channel, workflow_id={workflow.id})...")
        result = await runner.run_now(channel=channel, workflow_id=workflow.id)
        
        print(f"\n4. Результат:")
        print(f"   execution_id: {result.get('execution_id')}")
        print(f"   workflow_id: {result.get('workflow_id')}")
        print(f"   workflow_name: {result.get('workflow_name')}")
        print(f"   status: {result.get('status', 'not set')}")
        
        if 'error' in result:
            print(f"   error: {result['error']}")
        
        print("\n✅ Тест завершён!")
        
    finally:
        db.close()

asyncio.run(test_workflow())