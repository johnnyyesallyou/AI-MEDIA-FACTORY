import pathlib, py_compile

f = pathlib.Path('./backend/automation/runner.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Убираем RevisionJob и ReEvaluationJob из импорта
new_lines = []
for line in lines:
    if 'RevisionJob' in line or 'ReEvaluationJob' in line:
        print(f'  Удаляю строку: {line.strip()}')
        continue
    new_lines.append(line)

f.write_text('\n'.join(new_lines), encoding='utf-8')
print(f'\\n✅ Файл переписан ({len(new_lines)} строк)')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ runner.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')