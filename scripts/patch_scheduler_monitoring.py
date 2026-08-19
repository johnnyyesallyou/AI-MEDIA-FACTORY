import pathlib, py_compile

f = pathlib.Path('backend/automation/scheduler.py')
s = f.read_text(encoding='utf-8')
changes = 0

# 1. Add MonitoringJob import
if 'MonitoringJob' not in s:
    # Find the import section for jobs
    if 'from .jobs import' in s:
        # Find the line with jobs import and add MonitoringJob
        lines = s.split('\n')
        for i, line in enumerate(lines):
            if 'from .jobs import' in line:
                # Check if next lines are part of the import (parentheses)
                if '(' in line:
                    # Multi-line import, find the closing parenthesis
                    j = i
                    while j < len(lines) and ')' not in lines[j]:
                        j += 1
                    # Insert MonitoringJob before the closing paren
                    lines.insert(j, '    MonitoringJob,')
                    s = '\n'.join(lines)
                    changes += 1
                    print('  Added MonitoringJob to imports (multi-line)')
                    break
                else:
                    # Single-line import, add to the end
                    lines[i] = line.rstrip() + ', MonitoringJob'
                    s = '\n'.join(lines)
                    changes += 1
                    print('  Added MonitoringJob to imports (single-line)')
                    break
    else:
        # Add new import line
        s = s.replace(
            'from .jobs import',
            'from .jobs import MonitoringJob\nfrom .jobs import',
            1
        )
        changes += 1
        print('  Added MonitoringJob import')

# 2. Add monitoring job to scheduler setup
# Look for where other jobs are scheduled (e.g., add_job or scheduler.add_job)
if 'monitoring_job' not in s.lower() and 'MonitoringJob' not in s.split('add_job')[0] if 'add_job' in s else True:
    # Find where jobs are added to scheduler
    if 'scheduler.add_job' in s or '.add_job(' in s:
        # Find the last add_job call and add monitoring after it
        lines = s.split('\n')
        last_add_job_idx = -1
        for i, line in enumerate(lines):
            if 'add_job(' in line or 'scheduler.add_job' in line:
                last_add_job_idx = i
        
        if last_add_job_idx != -1:
            # Insert monitoring job after the last add_job
            indent = len(lines[last_add_job_idx]) - len(lines[last_add_job_idx].lstrip())
            monitoring_code = '\n' + ' ' * indent + '# Sprint 12: Monitoring job (every 10 minutes)\n'
            monitoring_code += ' ' * indent + 'scheduler.add_job(\n'
            monitoring_code += ' ' * indent + '    func=lambda: asyncio.to_thread(MonitoringJob().run),\n'
            monitoring_code += ' ' * indent + '    trigger="interval",\n'
            monitoring_code += ' ' * indent + '    minutes=10,\n'
            monitoring_code += ' ' * indent + '    id="monitoring_job",\n'
            monitoring_code += ' ' * indent + '    name="Monitoring (health + SLA)",\n'
            monitoring_code += ' ' * indent + '    replace_existing=True,\n'
            monitoring_code += ' ' * indent + '    max_instances=1,\n'
            monitoring_code += ' ' * indent + '    coalesce=True\n'
            monitoring_code += ' ' * indent + ')\n'
            
            lines.insert(last_add_job_idx + 1, monitoring_code)
            s = '\n'.join(lines)
            changes += 1
            print('  Added monitoring_job to scheduler (every 10 min)')
    else:
        print('  ⚠️ Could not find add_job pattern in scheduler.py')

if changes > 0:
    f.write_text(s, encoding='utf-8')
    try:
        py_compile.compile(str(f), doraise=True)
        print('  ✅✅✅ scheduler.py валиден')
    except py_compile.PyCompileError as e:
        print(f'  ❌ Ошибка: {e}')
else:
    print('  ℹ️ scheduler.py уже содержит monitoring_job или паттерн не найден')