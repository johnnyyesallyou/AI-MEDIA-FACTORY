import pathlib

f = pathlib.Path('backend/automation/scheduler.py')
content = f.read_text(encoding='utf-8')

# Заменяем CRLF на LF
if '\r\n' in content:
    print('Найдены CRLF, конвертируем в LF...')
    content = content.replace('\r\n', '\n')
    # Записываем в binary mode чтобы избежать авто-конвертации
    f.write_bytes(content.encode('utf-8'))
    print('✅ Файл конвертирован в LF (Unix-style)')
else:
    print('✅ Файл уже имеет LF окончания')

# Проверяем что файл компилируется
import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print('✅ py_compile: валиден')
except py_compile.PyCompileError as e:
    print(f'❌ py_compile: {e}')
