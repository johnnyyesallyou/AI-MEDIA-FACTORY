import pathlib, py_compile

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

print(f"Всего строк: {len(lines)}")

# Находим return блок (строки 490-498) и finally (строки 495-505)
return_start = None
return_end = None
finally_line = None

# Ищем return в 490-498
for i in range(490, min(498, len(lines))):
    stripped = lines[i].strip()
    if stripped.startswith('return {') and return_start is None:
        return_start = i
        print(f"   return start: строка {i+1}")
    elif return_start and stripped == '}' and return_end is None:
        return_end = i
        print(f"   return end: строка {i+1}")

# Ищем finally в 495-505 (после return)
for i in range(495, min(505, len(lines))):
    if lines[i].strip() == 'finally:':
        finally_line = i
        print(f"   finally: строка {i+1}")
        break

if not all([return_start, return_end, finally_line]):
    print(f"❌ Не найдены: return={return_start}, end={return_end}, finally={finally_line}")
    exit(1)

print(f"\nreturn блок: строки {return_start+1}-{return_end+1}")
print(f"finally: строка {finally_line+1}")

# Извлекаем return блок
return_block = lines[return_start:return_end+1]
print(f"\n📦 Извлечён return блок ({len(return_block)} строк)")

# Удаляем return блок
del lines[return_start:return_end+1]

# Находим новую позицию finally (должна быть меньше на длину return блока)
new_finally_line = None
for i in range(finally_line - len(return_block) - 5, finally_line + 5):
    if i >= 0 and i < len(lines) and lines[i].strip() == 'finally:':
        new_finally_line = i
        break

if new_finally_line is None:
    print("❌ Не найдена новая позиция finally")
    exit(1)

print(f"🔍 Новая позиция finally: строка {new_finally_line+1}")

# Находим конец finally блока
finally_end = new_finally_line + 1
for i in range(new_finally_line + 1, min(new_finally_line + 10, len(lines))):
    stripped = lines[i].strip()
    if not stripped or (stripped and len(lines[i]) - len(lines[i].lstrip()) <= 8):
        finally_end = i
        break

print(f"🔍 Конец finally блока: строка {finally_end+1}")

# Вставляем return блок ПОСЛЕ finally
for i, line in enumerate(return_block):
    lines.insert(finally_end + i, line)

print(f"\n✅ Return блок перемещён после finally")

p.write_text('\n'.join(lines), encoding='utf-8')

# Проверяем синтаксис
print("\n🧪 Проверяем синтаксис...")
try:
    py_compile.compile(str(p), doraise=True)
    print("✅✅✅ СИНТАКСИС ВАЛИДЕН! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")