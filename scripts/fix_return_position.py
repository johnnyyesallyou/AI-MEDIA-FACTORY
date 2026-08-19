import pathlib, py_compile

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

# Находим return блок (строки 493-497) и finally (строка 499)
return_start = None
return_end = None
finally_line = None

for i in range(490, 505):
    stripped = lines[i].strip()
    if stripped.startswith('return {') and return_start is None:
        return_start = i
    elif return_start and stripped == '}' and return_end is None:
        return_end = i
    elif stripped == 'finally:':
        finally_line = i

print(f"return блок: строки {return_start+1}-{return_end+1}")
print(f"finally: строка {finally_line+1}")

if not all([return_start, return_end, finally_line]):
    print("❌ Не найдены все блоки")
    exit(1)

# Извлекаем return блок
return_block = lines[return_start:return_end+1]
print(f"\n📦 Извлечён return блок ({len(return_block)} строк):")
for line in return_block:
    print(f"   {line}")

# Удаляем return блок из текущей позиции
del lines[return_start:return_end+1]

# Находим новую позицию finally (после удаления)
new_finally_line = None
for i in range(len(lines)):
    if lines[i].strip() == 'finally:':
        new_finally_line = i
        break

print(f"\n🔍 Новая позиция finally: строка {new_finally_line+1}")

# Находим конец finally блока (следующая пустая строка или следующая конструкция)
finally_end = new_finally_line + 1
for i in range(new_finally_line + 1, min(new_finally_line + 10, len(lines))):
    if not lines[i].strip():
        finally_end = i
        break
    elif lines[i].strip() and not lines[i].startswith('    ' * 3):  # не внутри finally
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