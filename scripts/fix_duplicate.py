import pathlib, py_compile

f = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем и удаляем дубликаты image_url в publisher.publish
new_lines = []
found_publish = False
skip_next_image_url = False

for i, line in enumerate(lines):
    # Если нашли publisher.publish
    if 'publisher.publish(' in line:
        found_publish = True
    
    # Если внутри publisher.publish и есть image_url
    if found_publish and 'image_url=' in line:
        # Проверяем есть ли уже image_url в следующих строках
        has_duplicate = False
        for j in range(i+1, min(i+10, len(lines))):
            if 'image_url=' in lines[j]:
                has_duplicate = True
                break
            if ')' in lines[j] and lines[j].strip() == ')':
                break
        
        if has_duplicate:
            print(f'  Пропускаю дубликат image_url на строке {i+1}: {line.strip()}')
            continue
    
    new_lines.append(line)

f.write_text('\n'.join(new_lines), encoding='utf-8')
print(f'✅ Файл переписан ({len(new_lines)} строк)')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ automation_jobs.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')
    # Показываем проблемные строки
    for i, line in enumerate(new_lines[580:595], start=581):
        print(f'{i}: {line}')