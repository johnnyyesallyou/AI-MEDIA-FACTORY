import pathlib, py_compile

f = pathlib.Path('backend/automation/jobs/__init__.py')
s = f.read_text(encoding='utf-8')

# Add import if missing
if 'from .monitoring_job import MonitoringJob' not in s:
    s = s.rstrip() + '\nfrom .monitoring_job import MonitoringJob\n'
    print('  Added MonitoringJob import')

# Add to __all__ if present and not already there
if '__all__' in s and '"MonitoringJob"' not in s and "'MonitoringJob'" not in s:
    s = s.replace('"ReEvaluationJob",', '"ReEvaluationJob",\n    "MonitoringJob",', 1)
    if '"MonitoringJob"' not in s:
        s = s.replace("'ReEvaluationJob',", "'ReEvaluationJob',\n    'MonitoringJob',", 1)
    print('  Added MonitoringJob to __all__')

f.write_text(s, encoding='utf-8')
try:
    py_compile.compile(str(f), doraise=True)
    print('  ✅ __init__.py валиден')
except py_compile.PyCompileError as e:
    print(f'  ❌ {e}')