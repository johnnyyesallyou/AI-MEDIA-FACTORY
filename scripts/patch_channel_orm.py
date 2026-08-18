import pathlib

p = pathlib.Path('./core/models/channel_orm.py')
s = p.read_text(encoding='utf-8')
changes = []

# Добавляем ForeignKey в import
if 'ForeignKey' not in s:
    s = s.replace(
        'from sqlalchemy import Column, String, Boolean, DateTime, JSON',
        'from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey'
    )
    changes.append('added ForeignKey import')

# Добавляем FK поля после workflow_id
if 'template_id' not in s:
    old_block = '    workflow_id = Column(String, nullable=True, index=True)'
    new_block = '''    workflow_id = Column(String, nullable=True, index=True)

    # Sprint 8.2: ссылки на шаблон и профиль
    template_id = Column(String, ForeignKey("channel_templates.id"), nullable=True, index=True)
    profile_id = Column(String, ForeignKey("channel_profiles.id"), nullable=True, index=True)'''
    if old_block in s:
        s = s.replace(old_block, new_block, 1)
        changes.append('added template_id, profile_id FK')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Ничего не изменилось')