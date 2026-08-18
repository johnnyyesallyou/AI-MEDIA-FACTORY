import pathlib, re

guard_file = pathlib.Path('./engines/writing/fact_guard.py')
s = guard_file.read_text(encoding='utf-8')

# Ищем весь остаток блока keywords (от "keywords = " до конца проверки matches)
# Удаляем всё что связано с keywords, matches, forbidden проверкой
old_block_pattern = r'''            keywords = \[\s*w for w in re\.findall\([^)]*\)\s*\].*?if keywords and matches == 0:.*?continue'''

match = re.search(old_block_pattern, s, re.DOTALL)
if match:
    # Полностью удаляем блок
    s = s[:match.start()] + s[match.end():]
    print(f"✅ Удалён блок keywords ({len(match.group(0))} символов)")
else:
    # Альтернативный подход: удаляем построчно
    lines = s.split('\n')
    new_lines = []
    skip = False
    removed_count = 0
    
    for i, line in enumerate(lines):
        # Начинаем пропуск когда видим keywords = [...]
        if 'keywords = [' in line and 're.findall' in line:
            skip = True
            removed_count += 1
            print(f"   Пропускаем строку {i+1}: {line.strip()}")
            continue
        
        # Заканчиваем пропуск когда видим "continue" после проверки matches
        if skip and 'continue' in line and i > 0:
            # Проверяем что это continue после if keywords and matches == 0
            if any('matches' in lines[j] for j in range(max(0, i-10), i)):
                removed_count += 1
                print(f"   Пропускаем строку {i+1}: {line.strip()}")
                skip = False
                continue
        
        # Пропускаем также строки внутри блока
        if skip:
            removed_count += 1
            continue
        
        new_lines.append(line)
    
    if removed_count > 0:
        s = '\n'.join(new_lines)
        print(f"✅ Удалено {removed_count} строк блока keywords")
    else:
        print("⚠️ Блок keywords не найден")

# Дополнительная очистка: удаляем пустые строки с неправильным отступом
lines = s.split('\n')
cleaned = []
for i, line in enumerate(lines):
    # Если строка содержит только пробелы (12 пробелов) и предыдущая/следующая строки имеют другой отступ
    if line.strip() == '' and line.startswith('            ') and len(line) > 12:
        # Проверяем контекст
        if i > 0 and i < len(lines) - 1:
            prev = lines[i-1]
            next_line = lines[i+1] if i+1 < len(lines) else ''
            # Если предыдущая строка - комментарий или другая строка, пропускаем пустую
            if prev.strip() and next_line.strip():
                print(f"   Удаляем пустую строку с отступом: строка {i+1}")
                continue
    cleaned.append(line)

s = '\n'.join(cleaned)

# Сохраняем
guard_file.write_text(s, encoding='utf-8')
print("\n✅ Файл сохранён")

# Проверяем синтаксис
import py_compile
try:
    py_compile.compile(str(guard_file), doraise=True)
    print("✅ Синтаксис валиден!")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка синтаксиса: {e}")
    # Показываем проблемные строки
    lines = s.split('\n')
    line_num = int(str(e).split('line ')[1].split(',')[0]) if 'line ' in str(e) else 162
    print(f"\n   Строки вокруг {line_num}:")
    for i in range(max(0, line_num-5), min(len(lines), line_num+5)):
        marker = ">>>" if i+1 == line_num else "   "
        print(f"   {i+1:4d} {marker}: {lines[i]}")