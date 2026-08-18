import pathlib, py_compile

f = pathlib.Path('./core/models/content_orm.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем весь блок с image_url, asset_id, image_prompt и удаляем его
# Будем пересоздавать правильно
new_lines = []
skip_until_close = False
paren_depth = 0
skip_fields = {'asset_id', 'image_prompt'}

i = 0
while i < len(lines):
    line = lines[i]
    
    # Пропускаем строки asset_id и image_prompt (они будут добавлены позже)
    stripped = line.strip()
    if any(stripped.startswith(f'{field} = Column') for field in skip_fields):
        print(f'Пропускаем строку {i+1}: {line.strip()}')
        i += 1
        continue
    
    # Обрабатываем image_url = Column(...)
    if 'image_url = Column(' in line:
        # Вставляем правильный блок
        new_lines.append('    asset_id = Column(String, ForeignKey("assets.id"), nullable=True)  # Sprint 11')
        new_lines.append('    image_url = Column(String(500), nullable=True)  # Sprint 11')
        new_lines.append('    image_prompt = Column(Text, nullable=True)  # Sprint 11')
        
        # Пропускаем оригинальное многострочное определение image_url
        j = i
        while j < len(lines):
            if ')' in lines[j] and not lines[j].strip().endswith(','):
                # Нашли закрывающую скобку
                break
            j += 1
        i = j + 1
        print('✅ Заменил блок image_url на правильный однострочный')
        continue
    
    new_lines.append(line)
    i += 1

f.write_text('\n'.join(new_lines), encoding='utf-8')
print(f'✅ Файл переписан ({len(new_lines)} строк)')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ content_orm.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')
    # Показываем проблемные строки
    for i, line in enumerate(new_lines[50:70], start=51):
        print(f'{i}: {line}')