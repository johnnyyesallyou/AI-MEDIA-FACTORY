import pathlib, re
p = pathlib.Path('./backend/automation/runner.py')
s = p.read_text(encoding='utf-8')
changes = []

# Ищем старый блок "if workflow_id:" который использует WorkflowEngineV2
# и заменяем его на WorkflowRuntime.execute()

# Шаблон: от "if workflow_id:" до "jobs = []  # Старый hardcoded список" (или похожего)
# Берём весь блок от if до конца jobs-построения
old_block = r'''(\s+)if workflow_id:
\1    logger\.info\(f"Loading workflow \{workflow_id\} from database"\)
\1    db = SessionLocal\(\)
\1    try:
\1        workflow_orm = db\.query\(WorkflowORM\)\.filter\(WorkflowORM\.id == workflow_id\)\.first\(\)
\1        if not workflow_orm:
\1            logger\.error\(f"Workflow \{workflow_id\} not found in database"\)
\1            result\["status"\] = "failed"
\1            result\["error"\] = f"Workflow \{workflow_id\} not found"
\1            return result
\1
\1        if not workflow_orm\.is_active:
\1            logger\.error\(f"Workflow \{workflow_id\} is not active"\)
\1            result\["status"\] = "failed"
\1            result\["error"\] = f"Workflow \{workflow_id\} is not active"
\1            return result
\1
\1        # Создаём WorkflowEngineV2
\1        engine = WorkflowEngineV2\(workflow_orm\.definition\)
\1
\1        # Валидируем workflow
\1        if not engine\.validate\(\):
\1            logger\.error\(f"Workflow \{workflow_id\} validation failed"\)
\1            result\["status"\] = "failed"
\1            result\["error"\] = f"Workflow \{workflow_id\} validation failed"
\1            return result
\1
\1        # Получаем порядок выполнения
\1        try:
\1            execution_order = engine\.get_execution_order\(\)
\1            logger\.info\(f"Execution order for workflow \{workflow_id\}: \{execution_order\}"\)
\1        except ValueError as e:
\1            logger\.error\(f"Workflow \{workflow_id\} has invalid graph: \{e\}"\)
\1            result\["status"\] = "failed"
\1            result\["error"\] = str\(e\)
\1            return result
\1
\1        # Строим список jobs из workflow
\1        jobs = \[\]
\1        for node_id in execution_order:
\1            node = engine\.get_node\(node_id\)
\1            node_type = node\.node_type
\1            # Ищем Job class для этого node_type
\1            job_class = self\.node_type_to_job\.get\(node_type\)
\1            if not job_class:
\1                logger\.warning\(f"No job class found for node_type '\{node_type\}', skipping node \{node_id\}"\)
\1                continue
\1            jobs\.append\(\(node_id, job_class\(\)\)\)
\1            logger\.info\(f"Added job: \{node_id\} \(type=\{node_type\}\)"\)
\1        result\["workflow_id"\] = workflow_id
\1        result\["workflow_name"\] = workflow_orm\.name
\1    finally:
\1        db\.close\(\)'''

new_block = r'''\1# Sprint 8.4.1: используем универсальный WorkflowRuntime
\1logger.info("Using WorkflowRuntime for workflow %s", workflow_id)
\1runtime = WorkflowRuntime()
\1runtime_result = await runtime.execute(
\1    workflow_id=workflow_id,
\1    channel=channel,
\1    execution_id=execution_id
\1)
\1
\1# Конвертируем ExecutionResult в старый формат для обратной совместимости
\1result["workflow_id"] = workflow_id
\1result["workflow_name"] = runtime_result.workflow_name
\1result["status"] = runtime_result.status
\1if runtime_result.error:
\1    result["error"] = runtime_result.error
\1
\1# Добавляем результаты каждой ноды
\1for node_id, node_result in runtime_result.node_results.items():
\1    result[node_id] = {
\1        "status": node_result.status.value,
\1        "output": node_result.output,
\1        "error": node_result.error,
\1        "metrics": node_result.metrics
\1    }
\1
\1# Пропускаем старую логику выполнения (jobs уже выполнены Runtime'ом)
\1jobs = []'''

# Пытаемся regex-замену
s_new, count = re.subn(old_block, new_block, s, count=1)

if count > 0:
    s = s_new
    changes.append(f'replaced WorkflowEngineV2 block with WorkflowRuntime.execute() (regex, {count} match)')
else:
    # Fallback: пробуем точную замену по строкам
    print("WARN: regex не сработал, пробуем точную замену")
    
    # Ищем маркер начала и конца
    start_marker = '        if workflow_id:\n            logger.info(f"Loading workflow {workflow_id} from database")'
    end_marker = '    finally:\n        db.close()'
    
    start_idx = s.find(start_marker)
    if start_idx != -1:
        # Ищем end_marker после start
        search_from = start_idx + len(start_marker)
        # Нам нужен тот end_marker который заканчивает блок try: (ищем следующий "finally:")
        # Ищем "    finally:" (4 пробела) после "    try:" блока
        end_search = s.find('        db.close()\n', search_from)
        if end_search != -1:
            end_idx = end_search + len('        db.close()\n')
            old_text = s[start_idx:end_idx]
            indent = '        '
            new_text = f'''{indent}# Sprint 8.4.1: используем универсальный WorkflowRuntime
{indent}logger.info("Using WorkflowRuntime for workflow %s", workflow_id)
{indent}runtime = WorkflowRuntime()
{indent}runtime_result = await runtime.execute(
{indent}    workflow_id=workflow_id,
{indent}    channel=channel,
{indent}    execution_id=execution_id
{indent})
{indent}
{indent}# Конвертируем ExecutionResult в старый формат
{indent}result["workflow_id"] = workflow_id
{indent}result["workflow_name"] = runtime_result.workflow_name
{indent}result["status"] = runtime_result.status
{indent}if runtime_result.error:
{indent}    result["error"] = runtime_result.error
{indent}for node_id, node_result in runtime_result.node_results.items():
{indent}    result[node_id] = {{
{indent}        "status": node_result.status.value,
{indent}        "output": node_result.output,
{indent}        "error": node_result.error,
{indent}        "metrics": node_result.metrics
{indent}    }}
{indent}jobs = []  # Runtime уже выполнил jobs
'''
            s = s[:start_idx] + new_text + s[end_idx:]
            changes.append('replaced via string-find fallback')
        else:
            print("ERROR: не найден end_marker")
    else:
        print("ERROR: не найден start_marker")

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применено {len(changes)} фиксов:')
    for c in changes:
        print(f'   ✅ {c}')
else:
    print('❌ Не удалось применить патч')