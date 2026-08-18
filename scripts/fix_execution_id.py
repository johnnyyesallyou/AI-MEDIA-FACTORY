import pathlib, re

p = pathlib.Path('./frontend/src/pages/Logs.tsx')
s = p.read_text(encoding='utf-8')

# Ищем интерфейс LogEntry и добавляем execution_id после id
# Regex: находим "interface LogEntry {" и следующие несколько строк с полями
pattern = re.compile(r'(interface\s+LogEntry\s*\{[^}]*?\n)(\s*id:\s*string;)')
m = pattern.search(s)
if m and 'execution_id' not in s:
    # Вставляем execution_id после id
    insert_point = m.end()
    s = s[:insert_point] + '\n  execution_id?: string;' + s[insert_point:]
    print('OK: execution_id added via regex')
elif 'execution_id' in s:
    print('INFO: execution_id already exists')
else:
    print('WARN: LogEntry interface not found')
    # Fallback: ищем просто "interface LogEntry"
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'interface LogEntry' in line:
            # Добавляем после следующей строки с id: string
            for j in range(i+1, min(i+10, len(lines))):
                if 'id: string' in lines[j]:
                    lines.insert(j+1, '  execution_id?: string;')
                    print(f'OK: execution_id added via fallback at line {j+1}')
                    break
            break
    s = '\n'.join(lines)

p.write_text(s, encoding='utf-8')