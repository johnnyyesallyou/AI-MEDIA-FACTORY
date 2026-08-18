import pathlib, py_compile

f = pathlib.Path('./core/models/content_orm.py')
s = f.read_text(encoding='utf-8')

changes = 0

# 1. Добавляем image_prompt
if 'image_prompt' not in s:
    s = s.replace(
        'image_url = Column(String',
        'image_url = Column(String(500), nullable=True)\n    image_prompt = Column(Text, nullable=True)  # Sprint 11',
        1
    )
    # Если image_url уже определён по-другому
    if 'image_prompt' not in s:
        lines = s.split('\n')
        for i, line in enumerate(lines):
            if 'image_url' in line and 'Column' in line:
                lines.insert(i+1, '    image_prompt = Column(Text, nullable=True)  # Sprint 11')
                changes += 1
                break
        s = '\n'.join(lines)
    else:
        changes += 1
    print('✅ Добавлен image_prompt')

# 2. Добавляем asset_id
if 'asset_id' not in s:
    s = s.replace(
        'image_url = Column(String',
        'asset_id = Column(String, ForeignKey("assets.id"), nullable=True)  # Sprint 11\n    image_url = Column(String',
        1
    )
    if 'asset_id' not in s:
        lines = s.split('\n')
        for i, line in enumerate(lines):
            if 'image_url' in line and 'Column' in line:
                lines.insert(i, '    asset_id = Column(String, ForeignKey("assets.id"), nullable=True)  # Sprint 11')
                changes += 1
                break
        s = '\n'.join(lines)
    else:
        changes += 1
    print('✅ Добавлен asset_id')

if changes > 0:
    f.write_text(s, encoding='utf-8')
else:
    print('ℹ️ Поля уже есть')

try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ content_orm.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')