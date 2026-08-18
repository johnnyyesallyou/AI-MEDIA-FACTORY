import pathlib
import py_compile

f = pathlib.Path('backend/automation/scheduler.py')
content = f.read_text(encoding='utf-8')

# Ищем строку с self.run_channel_automation
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if 'self.run_channel_automation' in line:
        # Показываем контекст (5 строк до и после)
        start = max(0, i - 6)
        end = min(len(lines), i + 5)
        print(f'\n=== Контекст строки {i} ===')
        for j in range(start, end):
            marker = '>>>' if j == i - 1 else '   '
            print(f'{marker} {j+1:4d}: {lines[j]}')
        
        # Проверяем предыдущие строки на пустые строки после открывающей скобки
        for k in range(i - 1, max(0, i - 10), -1):
            if lines[k].strip().startswith('self.scheduler.add_job('):
                if k + 1 < len(lines) and lines[k + 1].strip() == '':
                    print(f'\n❌ НАЙДЕНА ПРОБЛЕМА: пустая строка после {k+1}')
                break

print('\n=== Проверка компиляции ===')
try:
    py_compile.compile(str(f), doraise=True)
    print('✅ Файл компилируется без ошибок')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка компиляции: {e}')
