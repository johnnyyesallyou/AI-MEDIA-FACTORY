import pathlib, py_compile

f = pathlib.Path('./backend/automation/runner.py')
s = f.read_text(encoding='utf-8')

# Добавляем импорт ImageJob
if 'ImageJob' not in s:
    s = s.replace(
        'from .jobs import (',
        'from .jobs import (\n    ImageJob,'
    )
    print('✅ Добавлен импорт ImageJob')

# Добавляем ImageJob в stage_map
if '"image": ImageJob' not in s:
    s = s.replace(
        '"publish": PublishJob,',
        '"image": ImageJob,\n            "publish": PublishJob,'
    )
    print('✅ Добавлен image в stage_map')

# Добавляем ImageJob в node_type_to_job
if '"image": ImageJob' not in s and 'node_type_to_job' in s:
    s = s.replace(
        '"publisher": PublishJob,  # alias для publish',
        '"publisher": PublishJob,  # alias для publish\n            "image": ImageJob,'
    )
    print('✅ Добавлен image в node_type_to_job')

f.write_text(s, encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ runner.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')