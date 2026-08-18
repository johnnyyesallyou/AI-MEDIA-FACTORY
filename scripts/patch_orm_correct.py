import pathlib, py_compile

f = pathlib.Path('./core/models/content_orm.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Находим строку с image_url и добавляем поля ПОСЛЕ неё (учитывая многострочность)
image_url_line_idx = None
for i, line in enumerate(lines):
    if 'image_url' in line and 'Column' in line:
        image_url_line_idx = i
        print(f'Найден image_url на строке {i+1}: {line.strip()}')
        break

if image_url_line_idx:
    # Ищем конец определения image_url (может быть многострочным)
    j = image_url_line_idx
    while j < len(lines) and (')' not in lines[j] or lines[j].strip().endswith(',')):
        j += 1
        if ')' in lines[j-1] and not lines[j-1].strip().endswith(','):
            break
    
    print(f'Конец определения image_url на строке {j}')
    
    # Проверяем есть ли уже поля
    has_image_prompt = any('image_prompt' in line for line in lines)
    has_asset_id = any('asset_id' in line and 'Column' in line for line in lines)
    
    # Вставляем поля ПОСЛЕ image_url
    insert_idx = j
    fields_to_add = []
    
    if not has_image_prompt:
        fields_to_add.append('    image_prompt = Column(Text, nullable=True)  # Sprint 11')
        print('✅ Будет добавлен image_prompt')
    
    if not has_asset_id:
        fields_to_add.append('    asset_id = Column(String, ForeignKey("assets.id"), nullable=True)  # Sprint 11')
        print('✅ Будет добавлен asset_id')
    
    if fields_to_add:
        for field in reversed(fields_to_add):
            lines.insert(insert_idx, field)
        
        f.write_text('\n'.join(lines), encoding='utf-8')
        print(f'✅ Поля добавлены после строки {insert_idx}')
    else:
        print('ℹ️ Поля уже есть')
else:
    print('❌ image_url не найден')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ content_orm.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')