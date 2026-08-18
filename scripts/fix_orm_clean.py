import pathlib, py_compile

f = pathlib.Path('./core/models/content_orm.py')
lines = f.read_text(encoding='utf-8').split('\n')

new_lines = []
skip_next_n = 0
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Пропускаем "хвост" многострочного определения (String, nullable=True, ))
    # если предыдущая строка была нашей вставкой
    if stripped in ('String,', 'nullable=True', ')') and i > 0:
        prev_stripped = new_lines[-1].strip() if new_lines else ''
        # Если предыдущая строка — наш однострочный Column с # Sprint 11
        if prev_stripped.endswith('# Sprint 11'):
            print(f'  Убираю хвост на строке {i+1}: {line}')
            i += 1
            continue
    
    # Обрабатываем image_url = Column(  — заменяем на однострочный + пропускаем 3 строки хвоста
    if 'image_url = Column(' in line and line.strip().startswith('image_url = Column('):
        print(f'Заменяю многострочный image_url на строке {i+1}')
        # Пропускаем 3 следующие строки (String, nullable=True, ))
        i += 4  # +1 за текущую +3 за хвост
        continue
    
    # Пропускаем старые дубликаты (на всякий случай)
    if stripped.startswith('asset_id = Column') and '# Sprint 11' in stripped:
        print(f'  Убираю дубликат asset_id на строке {i+1}')
        i += 1
        continue
    if stripped.startswith('image_prompt = Column') and '# Sprint 11' in stripped:
        print(f'  Убираю дубликат image_prompt на строке {i+1}')
        i += 1
        continue
    if stripped.startswith('image_url = Column') and '# Sprint 11' in stripped:
        print(f'  Убираю дубликат image_url на строке {i+1}')
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

# Теперь проверяем есть ли все три поля и добавляем если нет
has_asset_id = any('asset_id = Column' in l and 'Sprint 11' in l for l in new_lines)
has_image_url = any('image_url = Column' in l and 'Sprint 11' in l for l in new_lines)
has_image_prompt = any('image_prompt = Column' in l and 'Sprint 11' in l for l in new_lines)

print(f'\\nПроверка полей:')
print(f'  asset_id: {has_asset_id}')
print(f'  image_url: {has_image_url}')
print(f'  image_prompt: {has_image_prompt}')

# Находим место для вставки — перед "# Telegram publishing metadata"
insert_idx = None
for i, line in enumerate(new_lines):
    if '# Telegram publishing metadata' in line:
        insert_idx = i
        break

if insert_idx and not (has_asset_id and has_image_url and has_image_prompt):
    fields = []
    if not has_asset_id:
        fields.append('    asset_id = Column(String, ForeignKey("assets.id"), nullable=True)  # Sprint 11')
    if not has_image_url:
        fields.append('    image_url = Column(String(500), nullable=True)  # Sprint 11')
    if not has_image_prompt:
        fields.append('    image_prompt = Column(Text, nullable=True)  # Sprint 11')
    
    for field in fields:
        new_lines.insert(insert_idx, field)
        insert_idx += 1
    print(f'✅ Добавлены недостающие поля перед строкой {insert_idx}')

f.write_text('\n'.join(new_lines), encoding='utf-8')
print(f'\\n✅ Файл переписан ({len(new_lines)} строк)')

# Показываем финальный результат
print('\\n=== Финальный результат (строки 50-70) ===')
for i, line in enumerate(new_lines[49:69], start=50):
    print(f'{i}: {line}')

try:
    py_compile.compile(str(f), doraise=True)
    print('\\n✅✅✅ content_orm.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'\\n❌ Ошибка: {e}')