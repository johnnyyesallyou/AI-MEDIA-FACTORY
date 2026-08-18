import pathlib

guard_file = pathlib.Path('./engines/writing/fact_guard.py')
s = guard_file.read_text(encoding='utf-8')

# Ищем текущую проверку (мой предыдущий фикс)
old_check = '''            # Sprint 8.5 fix: смягчаем проверку keywords
            # Разрешаем предложение если есть хотя бы 1 совпадение из 10 keywords
            # или если keywords очень мало (< 3)
            min_matches_required = max(1, len(keywords) // 10) if keywords else 0
            
            if keywords and matches < min_matches_required and len(keywords) >= 3:'''

new_check = '''            # Sprint 8.5 fix: максимально мягкая проверка keywords
            # Разрешаем предложение если:
            # - keywords < 5 (слишком мало для проверки)
            # - или matches >= 1 (хотя бы одно совпадение)
            # - или keywords >= 20 и matches >= 2 (для длинных текстов)
            if keywords and len(keywords) >= 5:
                min_matches_required = 1 if len(keywords) < 20 else 2
                if matches < min_matches_required:
                    logger.warning(
                        "Removed unsupported sentence (matches=%d/%d): %s",
                        matches, len(keywords), sentence[:100]
                    )
                    removed += 1
                    continue'''

if old_check in s:
    s = s.replace(old_check, new_check, 1)
    guard_file.write_text(s, encoding='utf-8')
    print("✅ FactGuard: разрешено 0 совпадений для < 5 keywords")
else:
    print("⚠️ Паттерн не найден")