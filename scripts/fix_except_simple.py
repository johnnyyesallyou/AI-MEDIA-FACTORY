import pathlib, py_compile

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

print(f"Всего строк в файле: {len(lines)}")

# Находим строки
try_line = None
except_line = None
finally_line = None

for i in range(len(lines)):
    stripped = lines[i].strip()
    if stripped == 'try:' and i >= 420 and try_line is None:
        try_line = i
    elif stripped.startswith('except ') and except_line is None:
        except_line = i
    elif stripped == 'finally:' and finally_line is None:
        finally_line = i

if not all([try_line, except_line, finally_line]):
    print(f"❌ Не найдены все блоки: try={try_line}, except={except_line}, finally={finally_line}")
    exit(1)

print(f"try:     строка {try_line + 1}, отступ: {len(lines[try_line]) - len(lines[try_line].lstrip())}")
print(f"except:  строка {except_line + 1}, отступ: {len(lines[except_line]) - len(lines[except_line].lstrip())}")
print(f"finally: строка {finally_line + 1}, отступ: {len(lines[finally_line]) - len(lines[finally_line].lstrip())}")

# Целевой отступ для try/except/finally
TARGET_INDENT = 8

# Текущий отступ except
current_except_indent = len(lines[except_line]) - len(lines[except_line].lstrip())
diff = current_except_indent - TARGET_INDENT

print(f"\n🔧 Фиксим except блок (строки {except_line+1}-{finally_line})...")
print(f"   Текущий отступ except: {current_except_indent}, целевой: {TARGET_INDENT}, разница: {diff}")

# Фиксим строку except и весь блок внутри
fixed = 0
for i in range(except_line, finally_line):
    line = lines[i]
    if not line.strip():
        continue
    
    current_indent = len(line) - len(line.lstrip())
    
    # Все строки в блоке except должны быть уменьшены на diff
    if current_indent >= current_except_indent:
        new_indent = max(TARGET_INDENT, current_indent - diff)
        lines[i] = ' ' * new_indent + line.lstrip()
        fixed += 1
        print(f"   L{i+1}: {current_indent}→{new_indent}")

p.write_text('\n'.join(lines), encoding='utf-8')
print(f"\n✅ Исправлено {fixed} строк")

# Проверяем синтаксис
print("\n🧪 Проверяем синтаксис...")
try:
    py_compile.compile(str(p), doraise=True)
    print("✅✅✅ СИНТАКСИС ВАЛИДЕН! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")