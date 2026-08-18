import pathlib, py_compile

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

# Жёстко ищем except на строке 478 (0-indexed: 477)
except_line = None
finally_line = None

for i in range(470, min(505, len(lines))):
    stripped = lines[i].strip()
    if stripped.startswith('except ') and except_line is None:
        except_line = i
    elif stripped == 'finally:' and except_line is not None and finally_line is None:
        finally_line = i

print(f"except строка: {except_line + 1}")
print(f"finally строка: {finally_line + 1}")

if except_line is None:
    print("❌ except не найден!")
    exit(1)

# Получаем текущий отступ except
current_except_indent = len(lines[except_line]) - len(lines[except_line].lstrip())
TARGET_INDENT = 12
diff = current_except_indent - TARGET_INDENT

print(f"Текущий отступ: {current_except_indent}, целевой: {TARGET_INDENT}, разница: {diff}")

# Фиксим весь блок от except до finally
fixed = 0
for i in range(except_line, finally_line if finally_line else len(lines)):
    line = lines[i]
    if not line.strip():
        continue
    
    current_indent = len(line) - len(line.lstrip())
    if current_indent >= current_except_indent:
        new_indent = max(TARGET_INDENT, current_indent - diff)
        lines[i] = ' ' * new_indent + line.lstrip()
        fixed += 1
        print(f"   L{i+1}: {current_indent}→{new_indent}")
    elif current_indent < TARGET_INDENT and i > except_line:
        # Вышли из блока - стоп
        break

p.write_text('\n'.join(lines), encoding='utf-8')
print(f"\n✅ Исправлено {fixed} строк")

# Проверяем синтаксис
try:
    py_compile.compile(str(p), doraise=True)
    print("✅✅✅ СИНТАКСИС ВАЛИДЕН! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")