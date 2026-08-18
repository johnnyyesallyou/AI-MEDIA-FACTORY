import pathlib

guard_file = pathlib.Path('./engines/writing/fact_guard.py')
s = guard_file.read_text(encoding='utf-8')
changes = []

# Ищем жёсткую проверку: "if keywords and matches == 0:"
old_check = '''            if keywords and matches == 0:

                logger.warning(
                    "Removed unsupported sentence: %s",
                    sentence
                )

                removed += 1
                continue'''

new_check = '''            # Sprint 8.5 fix: смягчаем проверку keywords
            # Разрешаем предложение если есть хотя бы 1 совпадение из 10 keywords
            # или если keywords очень мало (< 3)
            min_matches_required = max(1, len(keywords) // 10) if keywords else 0
            
            if keywords and matches < min_matches_required and len(keywords) >= 3:
                logger.warning(
                    "Removed unsupported sentence (matches=%d/%d): %s",
                    matches, len(keywords), sentence[:100]
                )
                removed += 1
                continue'''

if old_check in s:
    s = s.replace(old_check, new_check, 1)
    changes.append("FactGuard: смягчена проверка keywords (разрешено 1 совпадение из 10)")
else:
    print("⚠️ Точный паттерн не найден — показываю текущее состояние")
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'matches == 0' in line or 'keywords and matches' in line:
            print(f"   L{i+1}: {line}")

if changes:
    guard_file.write_text(s, encoding='utf-8')
    print(f"✅ Применено {len(changes)} фиксов:")
    for c in changes:
        print(f"   - {c}")
else:
    print("⚠️ Изменения не применены")