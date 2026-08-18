import pathlib

f = pathlib.Path('./frontend/src/components/ChannelManager.tsx')
lines = f.read_text(encoding='utf-8').split('\n')

# Удаляем строки 85-88 (0-indexed: 84-87) — это остатки сломанного блока
del lines[84:88]

f.write_text('\n'.join(lines), encoding='utf-8')
print("✅ Удалены строки 85-88 (остатки сломанного кода)")