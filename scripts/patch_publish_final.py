import pathlib, py_compile

f = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем строку с publisher.publish( и добавляем image_url
for i, line in enumerate(lines):
    if 'publisher.publish(' in line and 'text=full_text' in lines[i+1]:
        # Нашли вызов publisher.publish
        # Ищем где он заканчивается (закрывающая скобка)
        j = i
        paren_count = 0
        while j < len(lines):
            paren_count += lines[j].count('(') - lines[j].count(')')
            if paren_count == 0 and ')' in lines[j]:
                break
            j += 1
        
        # Вставляем image_url перед закрывающей скобкой
        # Находим последнюю строку с параметром
        for k in range(j, i, -1):
            if 'channel=channel' in lines[k] or 'credentials=credentials' in lines[k]:
                # Добавляем image_url
                indent = len(lines[k]) - len(lines[k].lstrip())
                new_line = ' ' * indent + 'image_url=getattr(item, "image_url", None),'
                lines.insert(k+1, new_line)
                print(f'✅ Добавлен image_url на строке {k+2}')
                break
        
        break

f.write_text('\n'.join(lines), encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ automation_jobs.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')