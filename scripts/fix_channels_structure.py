import pathlib, re
p = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = p.read_text(encoding='utf-8')
lines = s.split('\n')

# Ищем строку с "export default Channels;"
export_idx = None
for i, line in enumerate(lines):
    if 'export default Channels;' in line:
        export_idx = i
        break

if export_idx is None:
    print('ERROR: export default Channels; not found')
    exit(1)

print(f'Found export at line {export_idx + 1}')

# Ищем блок рендера ChannelManager (строки с showManagerModal)
modal_start = None
modal_end = None
for i in range(export_idx - 1, max(0, export_idx - 20), -1):
    if 'showManagerModal && managerChannel' in lines[i]:
        # Ищем начало блока (строка с {showManagerModal...)
        modal_start = i
        # Ищем конец блока (строка с закрывающей )})
        for j in range(i, min(len(lines), i + 15)):
            if lines[j].strip() == ')}':
                modal_end = j
                break
        break

if modal_start is None or modal_end is None:
    print('ERROR: ChannelManager render block not found')
    exit(1)

print(f'Found ChannelManager render at lines {modal_start + 1}-{modal_end + 1}')

# Удаляем блок рендера из текущего места
modal_block = lines[modal_start:modal_end + 1]
del lines[modal_start:modal_end + 1]

# Ищем правильное место для вставки — перед последним return statement
# Ищем строку с "</div>" и ");" перед export
insert_idx = None
for i in range(len(lines) - 1, max(0, len(lines) - 30), -1):
    if lines[i].strip() == '  );':
        # Это закрывающая скобка return statement
        # Вставляем ПЕРЕД ней
        insert_idx = i
        break

if insert_idx is None:
    print('ERROR: return statement not found')
    exit(1)

print(f'Inserting at line {insert_idx + 1} (before return statement)')

# Вставляем блок рендера в правильное место
lines.insert(insert_idx, '')
for j, modal_line in enumerate(modal_block):
    lines.insert(insert_idx + 1 + j, modal_line)

# Фиксим onSaved: loadAllSchedules -> loadChannels
new_lines = []
for line in lines:
    if 'onSaved={loadAllSchedules}' in line:
        line = line.replace('onSaved={loadAllSchedules}', 'onSaved={loadChannels}')
        print('Fixed onSaved: loadAllSchedules -> loadChannels')
    new_lines.append(line)

p.write_text('\n'.join(new_lines), encoding='utf-8')
print('✅ Структура исправлена')