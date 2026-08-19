import pathlib, py_compile

p = pathlib.Path('./backend/automation/runner.py')
s = p.read_text(encoding='utf-8')
lines = s.split('\n')

print(f"Всего строк в runner.py: {len(lines)}")

# Находим начало и конец метода run_now
start_idx = None
end_idx = None
method_indent = 0

for i, line in enumerate(lines):
    if '    async def run_now(self' in line:
        start_idx = i
        method_indent = len(line) - len(line.lstrip())
        print(f"   Начало run_now: строка {i+1}, indent={method_indent}")
    elif start_idx is not None and end_idx is None:
        stripped = line.lstrip()
        if stripped and not line.startswith(' ' * (method_indent + 1)):
            # Следующий метод или конец класса
            end_idx = i
            print(f"   Конец run_now: строка {i+1}")
            break

if start_idx is None:
    print("❌ run_now не найден!")
    exit(1)

if end_idx is None:
    end_idx = len(lines)

# Новый метод run_now
new_method = '''    async def run_now(self, channel=None, workflow_id: str = None) -> dict:
        """
        Sprint 8.4.1: Запускает pipeline для канала.
        Если workflow_id указан — делегирует WorkflowRuntime (универсальный исполнитель графов).
        Если не указан — fallback на hardcoded список (обратная совместимость).
        """
        execution_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        if channel:
            execution_id = f"{execution_id}-{channel.id}"

        logger.info("Automation started execution_id=%s channel=%s",
                    execution_id, getattr(channel, "name", None))

        result = {
            "execution_id": execution_id,
            "channel": {
                "id": getattr(channel, "id", None),
                "name": getattr(channel, "name", None),
                "platform": getattr(channel, "platform", None)
            } if channel else None
        }

        # Sprint 8.4.1: если есть workflow_id — делегируем WorkflowRuntime
        if workflow_id:
            logger.info("Using WorkflowRuntime for workflow %s", workflow_id)
            runtime = WorkflowRuntime()
            runtime_result = await runtime.execute(
                workflow_id=workflow_id,
                channel=channel,
                execution_id=execution_id
            )

            result["workflow_id"] = workflow_id
            result["workflow_name"] = runtime_result.workflow_name
            result["status"] = runtime_result.status
            if runtime_result.error:
                result["error"] = runtime_result.error

            for node_id, node_result in runtime_result.node_results.items():
                result[node_id] = {
                    "status": node_result.status.value,
                    "output": node_result.output,
                    "error": node_result.error,
                    "metrics": node_result.metrics
                }
            return result

        # Fallback: старый hardcoded список (для каналов без workflow_id)
        logger.info("No workflow_id provided, using hardcoded job list")
        jobs = [
            ("research", ResearchJob()),
            ("decision", DecisionJob()),
            ("writing", WritingJob()),
            ("evaluation", EvaluatorJob()),
            ("revision", RevisionJob()),
            ("re_evaluation", ReEvaluationJob()),
            ("publish", PublishJob()),
        ]

        for name, job in jobs:
            logger.info("Starting job=%s channel=%s", name, getattr(channel, "name", None))
            try:
                import inspect
                if inspect.iscoroutinefunction(job.run):
                    job_result = await job.run(channel=channel, execution_id=execution_id)
                else:
                    job_result = await asyncio.to_thread(job.run, channel=channel, execution_id=execution_id)
                result[name] = job_result
                logger.info("Job %s completed: %s", name, job_result.get("status", "unknown"))
            except Exception as e:
                logger.exception("Job %s failed", name)
                result[name] = {"status": "failed", "error": str(e)}
                result["status"] = "failed"
                break

        return result

'''

# Пересобираем файл
new_lines = lines[:start_idx] + new_method.split('\n') + lines[end_idx:]

# Убедимся что импорт WorkflowRuntime на месте
new_content = '\n'.join(new_lines)
if 'from .runtime import WorkflowRuntime' not in new_content:
    new_content = new_content.replace(
        'from .workflow_engine_v2 import WorkflowEngineV2',
        'from .workflow_engine_v2 import WorkflowEngineV2\nfrom .runtime import WorkflowRuntime'
    )
    print("✅ Добавлен импорт WorkflowRuntime")

p.write_text(new_content, encoding='utf-8')
print(f"✅ Метод run_now() переписан (строки {start_idx+1}-{end_idx})")

# Проверка синтаксиса
try:
    py_compile.compile(str(p), doraise=True)
    print('✅ Синтаксис runner.py валиден!')
except py_compile.PyCompileError as e:
    print(f'❌ Синтаксическая ошибка: {e}')
    exit(1)