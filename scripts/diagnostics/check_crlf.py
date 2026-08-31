import pathlib

# Путь ВНУТРИ контейнера
f = pathlib.Path('/app/backend/automation/scheduler.py')
content = f.read_bytes()

has_crlf = b'\r\n' in content
has_lf = b'\n' in content

print(f'Размер: {len(content)} bytes')
print(f'Has CRLF: {has_crlf}')
print(f'Has LF: {has_lf}')

if has_crlf:
    print('❌ Файл в контейнере имеет CRLF - это причина IndentationError!')
    # Пробуем пересоздать с LF
    text = content.decode('utf-8').replace('\r\n', '\n')
    f.write_bytes(text.encode('utf-8'))
    print('✅ Исправлено: CRLF заменены на LF')
else:
    print('✅ Файл в контейнере имеет правильные LF окончания')

# Показываем первые 200 байт в repr
print(f'\nПервые 200 байт (repr):')
print(repr(content[:200]))
