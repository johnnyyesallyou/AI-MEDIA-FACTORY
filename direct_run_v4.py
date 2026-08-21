import sys, asyncio, uuid
sys.path.insert(0, '/app')

# КЛЮЧЕВОЙ импорт — заполняет JobFactory в ЭТОМ процессе
import backend.automation.runtime.jobs_registry  # noqa

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from backend.automation.runtime.workflow_runtime import WorkflowRuntime
from backend.automation.runtime.job_factory import JobFactory

async def main():
    print('Registry in this process:', len(JobFactory._registry), 'types')
    
    db = SessionLocal()
    try:
        ch = db.query(ChannelORM).filter(ChannelORM.name == 'AI Anime News').first()
        if not ch:
            print('[!] Channel not found')
            return
        
        wf_id = ch.workflow_id or 'wf-simple'
        print(f'Channel: {ch.name} | Workflow: {wf_id}')
        
        runtime = WorkflowRuntime()
        exec_id = str(uuid.uuid4())
        print(f'Execution ID: {exec_id}\nRunning pipeline...\n')
        
        result = await runtime.execute(
            workflow_id=wf_id,
            channel=ch,
            execution_id=exec_id,
        )
        
        print('\n=== RESULT ===')
        print('Status:', result.status)
        for node_id, node_result in result.node_results.items():
            ok = "OK " if node_result.status == "success" else "ERR"
            print(f'  [{ok}] {node_id}: {node_result.status}')
            if node_result.error:
                print(f'        error: {node_result.error[:300]}')
    finally:
        db.close()

asyncio.run(main())