import pathlib, py_compile, re

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

# Находим все три строки
try_line = None
except_line = None
finally_line = None

for i in range(420, 510):
    stripped = lines[i].strip()
    if stripped == 'try:' and try_line is None:
        try_line = i
    elif stripped.startswith('except ') and except_line is None:
        except_line = i
    elif stripped == 'finally:' and finally_line is None:
        finally_line = i

print(f"try:     строка {try_line + 1}, отступ: {len(lines[try_line]) - len(lines[try_line].lstrip())}")
print(f"except:  строка {except_line + 1}, отступ: {len(lines[except_line]) - len(lines[except_line].lstrip())}")
print(f"finally: строка {finally_line + 1}, отступ: {len(lines[finally_line]) - len(lines[finally_line].lstrip())}")

TARGET_INDENT = 8  # Базовый отступ для try/except/finally
INNER_INDENT = 12  # Отступ для кода внутри блоков

# Фиксим саму строку except (приводим к отступу 8)
current_except_indent = len(lines[except_line]) - len(lines[except_line].lstrip())
diff = current_except_indent - TARGET_INDENT

print(f"\n🔧 Приводим except к отступу {TARGET_INDENT} (разница: {diff})...")

# Фиксим except и весь блок внутри него
for i in range(except_line, finally_line):
    line = lines[i]
    if not line.strip():
        continue
    
    current_indent = len(line) - len(line.lstrip())
    
    # Если это сама строка except или код внутри неё
    if current_indent >= current_except_indent:
        new_indent = max(TARGET_INDENT, current_indent - diff)
        lines[i] = ' ' * new_indent + line.lstrip()
        print(f"   L{i+1}: {current_indent}→{new_indent}: {line.lstrip()[:50]}")
    elif i == except_line:
        # Сама строка except
        lines[i] = ' ' * TARGET_INDENT + line.lstrip()
        print(f"   L{i+1}: {current_indent}→{TARGET_INDENT}: {line.lstrip()[:50]}")

p.write_text('\n'.join(lines), encoding='utf-8')
print(f"\n✅ Блок исправлен")

# Проверяем синтаксис
print("\n🧪 Проверяем синтаксис...")
try:
    py_compile.compile(str(p), doraise=True)
    print("✅✅✅ СИНТАКСИС ВАЛИДЕН! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")
    # Показываем problem area
    line_match = str(e).split('line ')[1].split(',')[0] if 'line ' in str(e) else None
    if line_match:
        line_num = int(''.join(c for c in line_match if c.isdigit()))
        print(f"\n   Строки вокруг {line_num}:")
        for i in range(max(0, line_num-5), min(len(lines), line_num+5)):
            indent = len(lines[i]) - len(lines[i].lstrip())
            marker = ">>>" if i+1 == line_num else "   "
            print(f"   {i+1:4d} [{indent:2}] {marker} {lines[i]}")