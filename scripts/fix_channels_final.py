import pathlib
p = pathlib.Path('./frontend/src/pages/Channels.tsx')
lines = p.read_text(encoding='utf-8').split('\n')

print("=== Анализ текущей структуры ===")

# 1. Удаляем неправильно вставленный блок (строки 199-206, 0-indexed: 198-205)
print("\n1. Удаляем неправильно вставленный блок (строки 199-206)...")
if len(lines) > 205 and 'showManagerModal' in lines[198]:
    del lines[198:206]  # удаляем 8 строк
    print("   ✅ Удалено")
else:
    print("   ❌ Блок не найден на ожидаемых позициях")

# 2. Ищем правильное место — перед последним </div> в return statement
print("\n2. Ищем правильное место для вставки...")
# Ищем строку с закрывающим </div> перед ");" и "};"
insert_before = None
for i in range(len(lines) - 1, max(0, len(lines) - 20), -1):
    if lines[i].strip() == '</div>':
        # Проверяем что после этой строки идут ");" и "};"
        for j in range(i + 1, min(len(lines), i + 5)):
            if ');' in lines[j] or lines[j].strip() == ');':
                insert_before = i
                break
        if insert_before:
            break

if insert_before is None:
    print("   ❌ Не найдено правильное место для вставки")
    exit(1)

print(f"   ✅ Найдено место перед строкой {insert_before + 1}: {lines[insert_before].strip()}")

# 3. Создаём блок модалки
modal_block = '''      {showManagerModal && managerChannel && (
        <ChannelManager
          channelId={managerChannel.id}
          channelName={managerChannel.name}
          onClose={() => { setShowManagerModal(false); setManagerChannel(null); }}
          onSaved={loadChannels}
        />
      )}'''

# 4. Вставляем ПЕРЕД найденной позицией
modal_lines = modal_block.split('\n')
for j, modal_line in enumerate(modal_lines):
    lines.insert(insert_before + j, modal_line)

print(f"   ✅ Вставлено {len(modal_lines)} строк перед строкой {insert_before + 1}")

# 5. Сохраняем
p.write_text('\n'.join(lines), encoding='utf-8')
print("\n✅ Файл сохранён")

# 6. Проверяем структуру
print("\n=== Проверка ===")
print(f"   Всего строк: {len(lines)}")
for i, line in enumerate(lines[195:210], start=196):
    print(f"   {i}: {line}")