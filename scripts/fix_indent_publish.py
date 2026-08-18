import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

# Ищем строку 463 и контекст вокруг неё
# Типичная проблема: новая строка имеет отступ 12 пробелов, а должна быть 8 или 16
fixed = False
for i in range(455, min(475, len(lines))):
    line = lines[i]
    # Если строка начинается с "publisher = " или "platform = " с неправильным отступом
    if 'publisher = PublisherFactory.get' in line or 'platform = getattr(channel' in line:
        # Проверяем отступ - должен быть 12 пробелов (внутри try блока)
        if not line.startswith('            '):
            # Фиксим отступ на 12 пробелов
            stripped = line.lstrip()
            lines[i] = '            ' + stripped
            print(f"   ✅ Исправлен отступ строки {i+1}")
            fixed = True

if fixed:
    p.write_text('\n'.join(lines), encoding='utf-8')
    print("✅ Отступы исправлены")
    
    # Проверяем синтаксис
    import py_compile
    try:
        py_compile.compile(str(p), doraise=True)
        print("✅ Синтаксис валиден!")
    except py_compile.PyCompileError as e:
        print(f"❌ Ошибка синтаксиса: {e}")
        # Показываем problem area
        line_num = int(str(e).split('line ')[1].split(',')[0]) if 'line ' in str(e) else 463
        print(f"\n   Строки вокруг {line_num}:")
        for i in range(max(0, line_num-5), min(len(lines), line_num+5)):
            marker = ">>>" if i+1 == line_num else "   "
            print(f"   {i+1:4d} {marker}: '{lines[i]}'")
else:
    print("⚠️ Не найдены строки для исправления")