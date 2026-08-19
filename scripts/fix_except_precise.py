import pathlib, py_compile

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

# Ищем ТОЛЬКО в нужном диапазоне
try_line = None
except_line = None
finally_line = None

# Ищем try в 420-470
for i in range(420, 470):
    if i < len(lines) and lines[i].strip() == 'try:':
        try_line = i
        break

# Ищем except в 470-490
for i in range(470, 490):
    if i < len(lines) and lines[i].strip().startswith('except '):
        except_line = i
        break

# Ищем finally в 495-507
for i in range(495, min(507, len(lines))):
    if lines[i].strip() == 'finally:':
        finally_line = i
        break

print(f"try:     строка {try_line + 1 if try_line else 'НЕ НАЙДЕНО'}")
print(f"except:  строка {except_line + 1 if except_line else 'НЕ НАЙДЕНО'}")
print(f"finally: строка {finally_line + 1 if finally_line else 'НЕ НАЙДЕНО'}")

if not all([try_line, except_line, finally_line]):
    print("❌ Не все блоки найдены в нужном диапазоне")
    exit(1)

try_indent = len(lines[try_line]) - len(lines[try_line].lstrip())
except_indent = len(lines[except_line]) - len(lines[except_line].lstrip())
finally_indent = len(lines[finally_line]) - len(lines[finally_line].lstrip())

print(f"\nТекущие отступы:")
print(f"   try:     {try_indent}")
print(f"   except:  {except_indent} (должен быть {try_indent})")
print(f"   finally: {finally_indent}")

if except_indent != try_indent:
    diff = except_indent - try_indent
    print(f"\n🔧 Фиксим блок except ({except_line+1}-{finally_line}), разница: {diff}")
    
    for i in range(except_line, finally_line):
        line = lines[i]
        if not line.strip():
            continue
        
        current_indent = len(line) - len(line.lstrip())
        if current_indent >= except_indent:
            new_indent = max(try_indent, current_indent - diff)
            lines[i] = ' ' * new_indent + line.lstrip()
            print(f"   L{i+1}: {current_indent}→{new_indent}")
    
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