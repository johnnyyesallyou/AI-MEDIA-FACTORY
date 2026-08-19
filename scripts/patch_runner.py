import pathlib, py_compile

f = pathlib.Path('backend/automation/runner.py')
s = f.read_text(encoding='utf-8')
changes = 0

# 1. Add MonitoringJob to imports
if 'MonitoringJob' not in s:
    s = s.replace(
        '    ReEvaluationJob,\n)',
        '    ReEvaluationJob,\n    MonitoringJob,\n)', 1
    )
    changes += 1
    print('  Added MonitoringJob to imports')

# 2. Add to stage_map
if '"monitoring": MonitoringJob' not in s:
    s = s.replace(
        '        "publish": PublishJob,\n    }',
        '        "publish": PublishJob,\n        "monitoring": MonitoringJob,\n    }', 1
    )
    changes += 1
    print('  Added monitoring to stage_map')

# 3. Add to node_type_to_job (if it exists)
if 'node_type_to_job' in s and '"monitoring": MonitoringJob' not in s:
    s = s.replace(
        '        "publisher": PublishJob,  # alias for publish',
        '        "publisher": PublishJob,  # alias for publish\n        "monitoring": MonitoringJob,', 1
    )
    changes += 1
    print('  Added monitoring to node_type_to_job')

if changes > 0:
    f.write_text(s, encoding='utf-8')
    try:
        py_compile.compile(str(f), doraise=True)
        print('  ✅ runner.py валиден')
    except py_compile.PyCompileError as e:
        print(f'  ❌ {e}')
else:
    print('  runner.py already has monitoring')