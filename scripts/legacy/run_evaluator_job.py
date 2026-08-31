import sys, asyncio
sys.path.insert(0, '/app')

from backend.automation.jobs.automation_jobs import EvaluatorJob

async def run_eval():
    job = EvaluatorJob()
    result = await job.run(channel=None, execution_id='manual-eval-001')
    print(f'\\n🎯 Результат EvaluatorJob:')
    print(f'   status: {result.get("status")}')
    print(f'   processed: {result.get("processed")}')
    print(f'   approved: {result.get("approved")}')
    print(f'   rejected: {result.get("rejected")}')
    if 'error' in result:
        print(f'   error: {result.get("error")}')

asyncio.run(run_eval())