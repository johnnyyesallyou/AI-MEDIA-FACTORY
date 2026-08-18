import pathlib, py_compile

f = pathlib.Path('backend/automation/scheduler.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Удаляем строки 111-113 (пустая + комментарий Sprint 12 + пустая)
# Ищем паттерн: self.scheduler.add_job( + пустая + # Sprint 12
new_lines = []
i = 0
removed = 0
while i < len(lines):
    line = lines[i]
    # Если это self.scheduler.add_job( и следующие 2 строки — пустая и комментарий Sprint 12
    if (line.strip() == 'self.scheduler.add_job(' and 
        i + 2 < len(lines) and 
        lines[i+1].strip() == '' and 
        'Sprint 12: Monitoring job' in lines[i+2]):
        print(f'  Удаляю строки {i+1}-{i+3}:')
        print(f'    {i+1}: {line}')
        print(f'    {i+2}: (пустая)')
        print(f'    {i+3}: {lines[i+2].strip()}')
        i += 3  # пропускаем 3 строки
        removed += 3
        continue
    new_lines.append(line)
    i += 1

print(f'\nУдалено строк: {removed}')

f.write_text('\n'.join(new_lines), encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ scheduler.py валиден')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')