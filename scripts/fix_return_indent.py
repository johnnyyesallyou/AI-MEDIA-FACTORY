import pathlib, py_compile

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

# Ищем строку "return {" в районе 490-500
return_line = None
for i in range(488, min(502, len(lines))):
    if lines[i].strip() == 'return {' or lines[i].strip().startswith('return {'):
        return_line = i
        break

if return_line is None:
    print("❌ return не найден")
    exit(1)

print(f"return на строке {return_line + 1}")
print(f"Текущий отступ: {len(lines[return_line]) - len(lines[return_line].lstrip())}")

# Приводим return к отступу 12
lines[return_line] = '            ' + lines[return_line].lstrip()  # 12 пробелов
print(f"✅ Приведён к отступу 12")

p.write_text('\n'.join(lines), encoding='utf-8')

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
        for i in range(max(0, line_num-3), min(len(lines), line_num+5)):
            indent = len(lines[i]) - len(lines[i].lstrip())
            marker = ">>>" if i+1 == line_num else "   "
            print(f"   {i+1:4d} [{indent:2}] {marker} {lines[i]}")