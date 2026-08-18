import pathlib, py_compile

f = pathlib.Path('./backend/automation/runner.py')
s = f.read_text(encoding='utf-8')

# Добавляем RevisionJob и ReEvaluationJob в импорт
if 'RevisionJob' not in s:
    s = s.replace(
        '    PublishJob,\n)',
        '    PublishJob,\n    RevisionJob,\n    ReEvaluationJob,\n)'
    )
    print('✅ Добавлены RevisionJob, ReEvaluationJob в импорт')

# Добавляем в stage_map
if '"revision": RevisionJob' not in s:
    s = s.replace(
        '            "publish": PublishJob,\n        }',
        '            "revision": RevisionJob,\n            "re_evaluation": ReEvaluationJob,\n            "publish": PublishJob,\n        }',
        1
    )
    print('✅ Добавлены в stage_map')

# Добавляем в node_type_to_job
if '"revision": RevisionJob' not in s and 'node_type_to_job' in s:
    s = s.replace(
        '            "publisher": PublishJob,  # alias для publish',
        '            "revision": RevisionJob,\n            "re_evaluation": ReEvaluationJob,\n            "publisher": PublishJob,  # alias для publish'
    )
    print('✅ Добавлены в node_type_to_job')

# Добавляем в hardcoded список (fallback)
if '("revision", RevisionJob())' not in s:
    s = s.replace(
        '            ("publish", PublishJob()),\n        ]',
        '            ("revision", RevisionJob()),\n            ("re_evaluation", ReEvaluationJob()),\n            ("publish", PublishJob()),\n        ]'
    )
    print('✅ Добавлены в hardcoded список')

f.write_text(s, encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ runner.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')