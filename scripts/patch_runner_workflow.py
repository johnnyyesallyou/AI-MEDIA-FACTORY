import pathlib

p = pathlib.Path('./backend/automation/runner.py')
s = p.read_text(encoding='utf-8')
changes = []

# 1. Добавляем импорт WorkflowEngineV2 и WorkflowRepository
old_import = '''from .jobs import (
    ResearchJob,
    DecisionJob,
    WritingJob,
    EvaluatorJob,
    PublishJob,
    RevisionJob,
    ReEvaluationJob,
)'''

new_import = '''from .jobs import (
    ResearchJob,
    DecisionJob,
    WritingJob,
    EvaluatorJob,
    PublishJob,
    RevisionJob,
    ReEvaluationJob,
)
from .workflow_engine_v2 import WorkflowEngineV2
from core.database import SessionLocal
from core.models.workflow_orm import WorkflowORM'''

if old_import in s and 'WorkflowEngineV2' not in s:
    s = s.replace(old_import, new_import, 1)
    changes.append('added imports for WorkflowEngineV2')

# 2. Добавляем маппинг node_type → Job class в __init__
old_init_end = '''        self.stage_map = {
            "research": ResearchJob,
            "decision": DecisionJob,
            "writing": WritingJob,
            "evaluation": EvaluatorJob,
            "revision": RevisionJob,
            "re_evaluation": ReEvaluationJob,
            "publish": PublishJob,
        }'''

new_init_end = '''        self.stage_map = {
            "research": ResearchJob,
            "decision": DecisionJob,
            "writing": WritingJob,
            "evaluation": EvaluatorJob,
            "revision": RevisionJob,
            "re_evaluation": ReEvaluationJob,
            "publish": PublishJob,
        }
        
        # Маппинг node_type (из workflow definition) на Job classes
        # Поддерживает разные названия: "writing" или "brief", "evaluator" или "evaluation"
        self.node_type_to_job = {
            "research": ResearchJob,
            "decision": DecisionJob,
            "writing": WritingJob,
            "brief": WritingJob,  # alias для writing
            "evaluation": EvaluatorJob,
            "evaluator": EvaluatorJob,  # alias для evaluation
            "revision": RevisionJob,
            "re_evaluation": ReEvaluationJob,
            "publish": PublishJob,
            "publisher": PublishJob,  # alias для publish
            # Future: "fact_checker": FactCheckJob, "image": ImageJob, etc.
        }'''

if old_init_end in s and 'node_type_to_job' not in s:
    s = s.replace(old_init_end, new_init_end, 1)
    changes.append('added node_type_to_job mapping')

# 3. Модифицируем run_now() для поддержки workflow_id
old_run_now_sig = '''    async def run_now(self, channel=None) -> dict:

        execution_id = datetime.utcnow().strftime(
            "%Y%m%d-%H%M%S"
        )'''

new_run_now_sig = '''    async def run_now(self, channel=None, workflow_id: str = None) -> dict:
        """
        Запускает полный pipeline для канала.
        
        Args:
            channel: объект канала (ChannelORM)
            workflow_id: ID workflow из БД (опционально).
                        Если указан, читает workflow из БД и выполняет динамически.
                        Если не указан, использует hardcoded список jobs (для обратной совместимости).
        
        Returns:
            dict с результатами выполнения
        """
        execution_id = datetime.utcnow().strftime(
            "%Y%m%d-%H%M%S"
        )'''

if old_run_now_sig in s and 'workflow_id: str = None' not in s:
    s = s.replace(old_run_now_sig, new_run_now_sig, 1)
    changes.append('added workflow_id parameter to run_now()')

# 4. Добавляем логику выбора workflow после инициализации result
old_result_init = '''        result = {
            "execution_id": execution_id,
            "channel": {
                "id": getattr(channel, "id", None),
                "name": getattr(channel, "name", None),
                "platform": getattr(channel, "platform", None)
            } if channel else None
        }


        jobs = [

            (
                "research",
                ResearchJob()
            ),'''

new_result_init = '''        result = {
            "execution_id": execution_id,
            "channel": {
                "id": getattr(channel, "id", None),
                "name": getattr(channel, "name", None),
                "platform": getattr(channel, "platform", None)
            } if channel else None
        }

        # Если workflow_id указан, читаем workflow из БД
        if workflow_id:
            logger.info(f"Loading workflow {workflow_id} from database")
            db = SessionLocal()
            try:
                workflow_orm = db.query(WorkflowORM).filter(WorkflowORM.id == workflow_id).first()
                if not workflow_orm:
                    logger.error(f"Workflow {workflow_id} not found in database")
                    result["status"] = "failed"
                    result["error"] = f"Workflow {workflow_id} not found"
                    return result
                
                if not workflow_orm.is_active:
                    logger.error(f"Workflow {workflow_id} is not active")
                    result["status"] = "failed"
                    result["error"] = f"Workflow {workflow_id} is not active"
                    return result
                
                # Создаём WorkflowEngineV2
                engine = WorkflowEngineV2(workflow_orm.definition)
                
                # Валидируем workflow
                if not engine.validate():
                    logger.error(f"Workflow {workflow_id} validation failed")
                    result["status"] = "failed"
                    result["error"] = f"Workflow {workflow_id} validation failed"
                    return result
                
                # Получаем порядок выполнения
                try:
                    execution_order = engine.get_execution_order()
                    logger.info(f"Execution order for workflow {workflow_id}: {execution_order}")
                except ValueError as e:
                    logger.error(f"Workflow {workflow_id} has invalid graph: {e}")
                    result["status"] = "failed"
                    result["error"] = str(e)
                    return result
                
                # Строим список jobs из workflow
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
                result["workflow_name"] = workflow_orm.name
                
            finally:
                db.close()
        else:
            # Старый hardcoded список jobs (для обратной совместимости)
            logger.info("No workflow_id provided, using hardcoded job list")
            jobs = [

                (
                    "research",
                    ResearchJob()
                ),'''

if old_result_init in s and 'workflow_id: str = None' in s and 'Loading workflow' not in s:
    s = s.replace(old_result_init, new_result_init, 1)
    changes.append('added workflow loading logic to run_now()')

# 5. Добавляем закрывающую скобку для else блока перед for loop
old_jobs_end = '''            (
                "publish",
                PublishJob()
            ),

        ]


        for name, job in jobs:'''

new_jobs_end = '''            (
                "publish",
                PublishJob()
            ),

            ]  # end of hardcoded jobs list

        # Выполняем jobs (из workflow или hardcoded)
        for name, job in jobs:'''

if old_jobs_end in s and 'end of hardcoded jobs list' not in s:
    s = s.replace(old_jobs_end, new_jobs_end, 1)
    changes.append('fixed jobs list structure')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'✅ Применено {len(changes)} фиксов:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Ничего не изменилось (патчи уже применены)')