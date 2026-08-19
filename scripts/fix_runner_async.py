import pathlib

p = pathlib.Path('./backend/automation/runner.py')
s = p.read_text(encoding='utf-8')
changed = []

if 'import asyncio' not in s:
    s = s.replace('import logging', 'import asyncio\nimport logging', 1)
    changed.append('import_asyncio')

# Заменяем вызов job.run в run_now: sync jobs -> to_thread
old_call = '''            try:

                job_result = job.run(
                    channel=channel,
                    execution_id=execution_id
                )


                import inspect

                if inspect.isawaitable(job_result):
                    job_result = await job_result


                result[name] = job_result'''

new_call = '''            try:

                import inspect

                if inspect.iscoroutinefunction(job.run):
                    # Async job (evaluator) — выполняем в event loop
                    job_result = await job.run(
                        channel=channel,
                        execution_id=execution_id
                    )
                else:
                    # Sync job (research/writing/publish) — в thread pool,
                    # чтобы НЕ блокировать event loop во время LLM-запросов
                    job_result = await asyncio.to_thread(
                        job.run,
                        channel=channel,
                        execution_id=execution_id
                    )

                result[name] = job_result'''

if old_call in s:
    s = s.replace(old_call, new_call)
    changed.append('run_now_to_thread')
else:
    print('WARN: run_now pattern not found')

# То же самое для retry_stage
old_retry = '''        try:
            job_result = job.run(channel=channel, execution_id=execution_id)
            import inspect
            if inspect.isawaitable(job_result):
                job_result = await job_result
            return job_result'''

new_retry = '''        try:
            import inspect
            if inspect.iscoroutinefunction(job.run):
                job_result = await job.run(channel=channel, execution_id=execution_id)
            else:
                job_result = await asyncio.to_thread(job.run, channel=channel, execution_id=execution_id)
            return job_result'''

if old_retry in s:
    s = s.replace(old_retry, new_retry)
    changed.append('retry_to_thread')

p.write_text(s, encoding='utf-8')
print(f'OK: runner patched: {", ".join(changed)}')