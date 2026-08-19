import sys, asyncio, traceback
sys.path.insert(0, '/app')

log_file = open('/tmp/eval_result.txt', 'w', encoding='utf-8')

def log(msg):
    print(msg)
    log_file.write(str(msg) + '\n')
    log_file.flush()

async def run_eval():
    try:
        log('=== Импорт EvaluatorJob ===')
        from backend.automation.jobs.automation_jobs import EvaluatorJob
        log('✅ Импорт успешен')
        
        log('\\n=== Создание job ===')
        job = EvaluatorJob()
        log(f'✅ Job создан: {job.__class__.__name__}')
        
        log('\\n=== Запуск job.run() ===')
        result = await job.run(channel=None, execution_id='manual-eval-001')
        
        log('\\n=== Результат EvaluatorJob ===')
        for key, value in result.items():
            log(f'   {key}: {value}')
        
    except Exception as e:
        log(f'\\n❌ КРИТИЧЕСКАЯ ОШИБКА: {type(e).__name__}: {e}')
        log('\\nTraceback:')
        log(traceback.format_exc())

try:
    asyncio.run(run_eval())
finally:
    log_file.close()
    log('\\n=== Завершено, лог сохранён в /tmp/eval_result.txt ===')