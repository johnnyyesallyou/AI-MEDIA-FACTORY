import pathlib
p = pathlib.Path('./backend/app/api/v1/content.py')
s = p.read_text(encoding='utf-8')

# Ищем все места, где перечислены статусы, и добавляем needs_revision
patterns = [
    ('"draft", "review", "approved"', '"draft", "review", "needs_revision", "approved"'),
    ('"draft", "approved"', '"draft", "needs_revision", "approved"'),
    ('status: str = Query', 'status: str = Query'),
]

for old, new in patterns:
    if old in s and old != new:
        s = s.replace(old, new)
        print(f'OK: replaced "{old}" -> "{new}"')

p.write_text(s, encoding='utf-8')
print('✅ content.py updated')