import pathlib, py_compile

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

# Строки которые должны быть с отступом 12 (на уровне try), а не 20 (внутри if)
# Это всё что идёт ПОСЛЕ continue в блоке "if not result.success"
fixed_count = 0
in_publish_try_block = False

for i in range(455, min(485, len(lines))):
    line = lines[i]
    
    # Ищем строку "continue" после "if not result.success"
    if 'if not result.success' in line:
        in_publish_try_block = True
        continue
    
    # После continue (строка 461) следующие строки должны иметь отступ 12
    if in_publish_try_block and line.strip() == 'continue':
        # Следующие непустые строки должны быть с отступом 12
        for j in range(i+1, min(i+15, len(lines))):
            next_line = lines[j]
            if not next_line.strip():  # пустая строка - пропускаем
                continue
            # Если строка начинается с 20 пробелов - меняем на 12
            if next_line.startswith('                    ') and not next_line.startswith('                        '):
                # Это строка с отступом 20 - должна быть 12
                stripped = next_line.lstrip()
                # Проверяем что это не вложенная конструкция (logger.info, if, for)
                if stripped.startswith(('item.', 'db.', 'published', 'logger.info')):
                    lines[j] = '            ' + stripped  # 12 пробелов
                    fixed_count += 1
                    print(f"   ✅ L{j+1}: 20→12 пробелов: {stripped[:60]}")
            elif next_line.startswith('            '):
                # Уже правильный отступ - выходим
                break
            else:
                # Другой отступ - пропускаем
                break
        break

if fixed_count > 0:
    p.write_text('\n'.join(lines), encoding='utf-8')
    print(f"\n✅ Исправлено {fixed_count} строк")
else:
    print("⚠️ Ничего не исправлено — показываю problem area:")
    for i in range(460, min(475, len(lines))):
        print(f"   {i+1:4d}: '{lines[i]}'")

# Проверяем синтаксис
print("\n🧪 Проверяем синтаксис...")
try:
    py_compile.compile(str(p), doraise=True)
    print("✅ Синтаксис валиден!")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")
    # Показываем problem area
    line_num = int(str(e).split('line ')[1].split(',')[0]) if 'line ' in str(e) else 463
    print(f"\n   Строки вокруг {line_num}:")
    for i in range(max(0, line_num-3), min(len(lines), line_num+5)):
        marker = ">>>" if i+1 == line_num else "   "
        print(f"   {i+1:4d} {marker}: '{lines[i]}'")