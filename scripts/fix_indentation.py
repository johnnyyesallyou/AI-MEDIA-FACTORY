import pathlib

guard_file = pathlib.Path('./engines/writing/fact_guard.py')
lines = guard_file.read_text(encoding='utf-8').split('\n')

# Ищем строку 162 и исправляем отступ
# Типичная проблема: строка с неправильным отступом после удаления блока
fixed = False
for i in range(155, min(175, len(lines))):
    line = lines[i]
    # Если строка пустая или содержит только пробелы с неправильным отступом
    if line.strip() == '' or (line.startswith('    ') and not line.startswith('        ')):
        # Проверяем контекст - предыдущая и следующая строки
        if i > 0 and i < len(lines) - 1:
            prev_line = lines[i-1]
            next_line = lines[i+1]
            
            # Если предыдущая строка имеет отступ 12 пробелов, а текущая 4 - это проблема
            if prev_line.startswith('            ') and line.startswith('    ') and not line.strip():
                # Удаляем пустую строку с неправильным отступом
                lines[i] = ''
                fixed = True
                print(f"   ✅ Исправлена пустая строка {i+1}")

if fixed:
    guard_file.write_text('\n'.join(lines), encoding='utf-8')
    print("✅ IndentationError исправлен")
else:
    print("⚠️ Не найдена проблема — показываю строки 158-168:")
    for i in range(157, min(168, len(lines))):
        print(f"   {i+1:4d}: '{lines[i]}'")