import pathlib, py_compile

f = pathlib.Path('./backend/automation/runner.py')
s = f.read_text(encoding='utf-8')

# Убираем revision и re_evaluation из stage_map
if '"revision": RevisionJob' in s:
    s = s.replace('            "revision": RevisionJob,\n', '')
    print('✅ Убран revision из stage_map')

if '"re_evaluation": ReEvaluationJob' in s:
    s = s.replace('            "re_evaluation": ReEvaluationJob,\n', '')
    print('✅ Убран re_evaluation из stage_map')

# Убираем из node_type_to_job
if '"revision": RevisionJob' in s:
    s = s.replace('            "revision": RevisionJob,\n', '')
    print('✅ Убран revision из node_type_to_job')

if '"re_evaluation": ReEvaluationJob' in s:
    s = s.replace('            "re_evaluation": ReEvaluationJob,\n', '')
    print('✅ Убран re_evaluation из node_type_to_job')

f.write_text(s, encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ runner.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')