import sys, asyncio, uuid, inspect
sys.path.insert(0, '/app')

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.workflow_orm import WorkflowORM
from backend.automation.runtime.workflow_runtime import WorkflowRuntime

async def main():
    db = SessionLocal()
    try:
        ch = db.query(ChannelORM).filter(ChannelORM.name == 'AI Anime News').first()
        if not ch:
            print('[!] Channel not found')
            return
        
        wf_id = ch.workflow_id or 'wf-simple'
        wf = db.query(WorkflowORM).filter(WorkflowORM.id == wf_id).first()
        if not wf:
            print(f'[!] Workflow {wf_id!r} not found')
            return
        
        print(f'Channel: {ch.name} ({ch.id})')
        print(f'Workflow: {wf.name} ({wf_id})')
        print(f'Nodes: {[n["type"] for n in wf.definition.get("nodes", [])]}')
        
        # Проверяем сигнатуру execute
        runtime = WorkflowRuntime()
        sig = inspect.signature(runtime.execute)
        print(f'\nWorkflowRuntime.execute signature: {sig}')
        print(f'Parameters: {list(sig.parameters.keys())}')
        
        exec_id = str(uuid.uuid4())
        print(f'\nExecution ID: {exec_id}')
        print('Running pipeline...\n')
        
        # Пробуем разные варианты вызова
        try:
            # Вариант 1: workflow_definition, channel, execution_id
            result = await runtime.execute(
                workflow_definition=wf.definition,
                channel=ch,
                execution_id=exec_id,
            )
        except TypeError as e1:
            print(f'Attempt 1 failed: {e1}')
            try:
                # Вариант 2: definition, channel
                result = await runtime.execute(
                    definition=wf.definition,
                    channel=ch,
                    execution_id=exec_id,
                )
            except TypeError as e2:
                print(f'Attempt 2 failed: {e2}')
                try:
                    # Вариант 3: positional
                    result = await runtime.execute(wf.definition, ch, exec_id)
                except TypeError as e3:
                    print(f'Attempt 3 failed: {e3}')
                    return
        
        print(f'\n=== RESULT ===')
        print(f'Status: {result.status}')
        if hasattr(result, 'node_results'):
            for node_id, node_result in result.node_results.items():
                status = "✓" if node_result.status == "success" else "✗"
                print(f'  {status} {node_id}: {node_result.status}')
                if node_result.error:
                    print(f'      error: {node_result.error[:200]}')
    finally:
        db.close()

asyncio.run(main())