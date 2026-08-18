import pathlib

p = pathlib.Path('./backend/app/api/v1/templates.py')
s = p.read_text(encoding='utf-8')
changes = []

# ФИКС: channel_repo.get_by_id → channel_repo.get
if 'channel_repo.get_by_id' in s:
    s = s.replace('channel_repo.get_by_id', 'channel_repo.get')
    changes.append('channel_repo.get_by_id → channel_repo.get')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Ничего не изменилось')