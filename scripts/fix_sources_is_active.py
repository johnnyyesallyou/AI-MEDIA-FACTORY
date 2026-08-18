import pathlib
p = pathlib.Path('./backend/app/api/v1/channels.py')
s = p.read_text(encoding='utf-8')
changes = []

# Ищем проблемную строку с is_active=s["is_active"]
old_line = '        url=s["url"], priority=s["priority"], is_active=s["is_active"],'
new_line = '        url=s["url"], priority=s["priority"], is_active=s.get("is_active", True),'

if old_line in s:
    s = s.replace(old_line, new_line, 1)
    changes.append('fixed is_active with .get() and default True')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'✅ Применены фиксы:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Ничего не изменилось (патч уже применён или отличается)')