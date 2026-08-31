import pathlib
p = pathlib.Path('./frontend/src/pages/Logs.tsx')
lines = p.read_text(encoding='utf-8').split('\n')

# Находим строку с "id: string;" в интерфейсе LogEntry и добавляем после неё execution_id
in_interface = False
fixed = False
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if 'interface LogEntry' in line:
        in_interface = True
    if in_interface and 'id: string;' in line and 'execution_id' not in lines[i+1]:
        new_lines.append('  execution_id?: string;')
        fixed = True
        in_interface = False

if fixed:
    p.write_text('\n'.join(new_lines), encoding='utf-8')
    print('OK: execution_id added to LogEntry interface')
else:
    print('INFO: already fixed or not needed')