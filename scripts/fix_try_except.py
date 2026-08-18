import pathlib, py_compile

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

# Находим строки try, for, except
try_line = None
for_line = None
except_line = None
finally_line = None

for i in range(430, 500):
    stripped = lines[i].strip()
    if stripped == 'try:':
        try_line = i
    elif 'for item in items' in stripped or 'for debug_item in items' in stripped:
        for_line = i
    elif stripped.startswith('except Exception'):
        except_line = i
    elif stripped == 'finally:':
        finally_line = i

print(f"try:     строка {try_line + 1 if try_line else 'не найдено'}")
print(f"for:     строка {for_line + 1 if for_line else 'не найдено'}")
print(f"except:  строка {except_line + 1 if except_line else 'не найдено'}")
print(f"finally: строка {finally_line + 1 if finally_line else 'не найдено'}")

if try_line is None or except_line is None:
    print("❌ Не найдены try или except")
    exit(1)

# Получаем отступ try
try_indent = len(lines[try_line]) - len(lines[try_line].lstrip())
except_indent = len(lines[except_line]) - len(lines[except_line].lstrip())

print(f"\ntry отступ:    {try_indent} пробелов")
print(f"except отступ: {except_indent} пробелов (должен быть {try_indent})")

if try_indent != except_indent:
    # Фиксим except и весь блок после него до finally
    print(f"\n🔧 Фиксим except блок (строки {except_line+1} до {finally_line+1 if finally_line else 'конец'})...")
    
    diff = except_indent - try_indent  # разница которую нужно вычесть
    
    for i in range(except_line, finally_line if finally_line else len(lines)):
        line = lines[i]
        if not line.strip():  # пустая строка
            continue
        
        current_indent = len(line) - len(line.lstrip())
        if current_indent >= except_indent:
            # Уменьшаем отступ на diff
            new_indent = max(try_indent, current_indent - diff)
            stripped = line.lstrip()
            lines[i] = ' ' * new_indent + stripped
            print(f"   L{i+1}: {current_indent}→{new_indent}: {stripped[:50]}")
    
    p.write_text('\n'.join(lines), encoding='utf-8')
    print(f"\n✅ Блок исправлен")
else:
    print("✅ Отступы уже правильные")

# Проверяем синтаксис
print("\n🧪 Проверяем синтаксис...")
try:
    py_compile.compile(str(p), doraise=True)
    print("✅ Синтаксис валиден!")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")