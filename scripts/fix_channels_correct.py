import pathlib, re
p = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = p.read_text(encoding='utf-8')
lines = s.split('\n')

print("=== Анализ текущей структуры ===")

# 1. Находим и удаляем неправильно вставленный блок ChannelManager
print("\n1. Ищем неправильно вставленный ChannelManager...")
orphan_start = None
orphan_end = None

for i, line in enumerate(lines):
    if '{showManagerModal && managerChannel && (' in line:
        # Проверяем, не находится ли он внутри другого JSX (отступ больше 6 пробелов)
        indent = len(line) - len(line.lstrip())
        print(f"   Найден на строке {i+1}, indent={indent}")
        
        # Ищем конец блока (строка с )})
        for j in range(i, min(len(lines), i + 15)):
            if lines[j].strip() == ')}':
                orphan_end = j
                orphan_start = i
                print(f"   Конец блока на строке {j+1}")
                break
        break

if orphan_start is not None and orphan_end is not None:
    print(f"   Удаляем строки {orphan_start+1}-{orphan_end+1}")
    del lines[orphan_start:orphan_end + 1]
else:
    print("   ❌ Неправильно вставленный блок не найден")

# 2. Ищем ПРАВИЛЬНУЮ позицию для вставки
print("\n2. Ищем правильную позицию для вставки...")

# Ищем первый return statement компонента
return_line = None
for i, line in enumerate(lines):
    if re.match(r'^\s*return\s*\(', line):
        return_line = i
        print(f"   Найден return на строке {i+1}: {line.strip()}")
        break

if return_line is None:
    print("   ❌ Return statement не найден")
    exit(1)

# Вставляем ПОСЛЕ return ( (строка с открывающей скобкой)
# Ищем строку с return (
insert_after = return_line
for i in range(return_line, min(len(lines), return_line + 5)):
    if '(' in lines[i]:
        insert_after = i
        break

print(f"   Вставляем после строки {insert_after + 1}")

# 3. Создаём блок модалки
modal_block = '''      {showManagerModal && managerChannel && (
        <ChannelManager
          channelId={managerChannel.id}
          channelName={managerChannel.name}
          onClose={() => { setShowManagerModal(false); setManagerChannel(null); }}
          onSaved={loadChannels}
        />
      )}'''

# 4. Вставляем
modal_lines = modal_block.split('\n')
for j, modal_line in enumerate(modal_lines):
    lines.insert(insert_after + 1 + j, modal_line)

print(f"   ✅ Вставлено {len(modal_lines)} строк после строки {insert_after + 1}")

# 5. Сохраняем
p.write_text('\n'.join(lines), encoding='utf-8')
print("\n✅ Файл сохранён")

# 6. Проверяем
print("\n=== Проверка ===")
print(f"   Всего строк: {len(lines)}")
print(f"   showManagerModal использований: {sum(1 for l in lines if 'showManagerModal' in l)}")
print(f"   ChannelManager использований: {sum(1 for l in lines if '<ChannelManager' in l)}")