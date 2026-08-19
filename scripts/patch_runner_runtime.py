import pathlib
import re
p = pathlib.Path('./backend/automation/runner.py')
s = p.read_text(encoding='utf-8')
changes = []

# 1. Добавляем импорт WorkflowRuntime
if 'from .runtime import WorkflowRuntime' not in s:
    old_import = '''from .workflow_engine_v2 import WorkflowEngineV2
from core.database import SessionLocal
from core.models.workflow_orm import WorkflowORM'''
    
    new_import = '''from .workflow_engine_v2 import WorkflowEngineV2
from .runtime import WorkflowRuntime
from core.database import SessionLocal
from core.models.workflow_orm import WorkflowORM'''
    
    if old_import in s:
        s = s.replace(old_import, new_import, 1)
        changes.append('added WorkflowRuntime import')

# 2. Модифицируем run_now() для использования WorkflowRuntime
# Ищем блок "if workflow_id:" и заменяем логику выполнения
old_workflow_exec = '''            # Строим список jobs из workflow
            jobs = []
            for node_id in execution_order:
                node = engine.get_node(node_id)
                node_type = node.node_type
                # Ищем Job class для этого node_type
                job_class = self.node_type_to_job.get(node_type)
                if not job_class:
                    logger.warning(f"No job class found for node_type '{node_type}', skipping node {node_id}")
                    continue
                jobs.append((node_id, job_class()))
                logger.info(f"Added job: {node_id} (type={node_type})")
            result["workflow_id"] = workflow_id
            result["workflow_name"] = workflow_orm.name'''

new_workflow_exec = '''            # Sprint 8.4.1: используем универсальный WorkflowRuntime
            logger.info("Using WorkflowRuntime for workflow %s", workflow_id)
            runtime = WorkflowRuntime()
            runtime_result = await runtime.execute(
                workflow_id=workflow_id,
                channel=channel,
                execution_id=execution_id
            )
            
            # Конвертируем ExecutionResult в старый формат для обратной совместимости
            result["workflow_id"] = workflow_id
            result["workflow_name"] = workflow_orm.name
            result["status"] = runtime_result.status
            
            # Добавляем результаты каждой ноды
            for node_id, node_result in runtime_result.node_results.items():
                result[node_id] = {
                    "status": node_result.status.value,
                    "output": node_result.output,
                    "error": node_result.error,
                    "metrics": node_result.metrics
                }
            
            # Пропускаем старую логику выполнения jobs
            jobs = []  # Пустой список — runtime уже всё выполнил'''

if old_workflow_exec in s and 'Using WorkflowRuntime' not in s:
    s = s.replace(old_workflow_exec, new_workflow_exec, 1)
    changes.append('replaced job execution with WorkflowRuntime.execute()')

# 3. Для обратной совместимости (workflow_id=None) оставляем старый код
# Но добавляем комментарий что это legacy path
if 'else:' in s and '# Старый hardcoded список jobs' not in s:
    s = s.replace(
        '    else:\n        # Старый hardcoded список jobs',
        '    else:\n        # Sprint 8.4.1: Legacy path для обратной совместимости\n        # (каналы без workflow_id используют старый hardcoded список)',
        1
    )
    changes.append('added legacy path comment')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'✅ Применено {len(changes)} фиксов:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Ничего не изменилось (патчи уже применены)')