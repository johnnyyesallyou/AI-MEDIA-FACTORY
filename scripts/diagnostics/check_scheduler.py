import pathlib
f = pathlib.Path('backend/automation/scheduler.py')
lines = f.read_text(encoding='utf-8').split('\n')
print(f'Total lines: {len(lines)}')
print()

# Ищем проблему
for i, line in enumerate(lines, 1):
    if 'IndentationError' in line or 'unexpected indent' in line:
        print(f'Line {i} [ERROR]: {repr(line)}')
    elif i >= 105 and i <= 125:
        # Показываем проблемную область с repr чтобы увидеть табы/пробелы
        print(f'{i:4d}: {repr(line[:80])}')
