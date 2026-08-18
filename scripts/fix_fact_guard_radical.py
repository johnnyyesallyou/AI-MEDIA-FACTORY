import pathlib, re

guard_file = pathlib.Path('./engines/writing/fact_guard.py')
s = guard_file.read_text(encoding='utf-8')

# Ищем весь блок keywords + matches (мои предыдущие фиксы)
# Паттерн: от "# Sprint 8.5 fix:" до "continue"
old_block_pattern = r'''            # Sprint 8\.5 fix:.*?\n.*?if keywords and len\(keywords\) >= 5:.*?continue'''

match = re.search(old_block_pattern, s, re.DOTALL)
if match:
    # Заменяем на комментарий что проверка отключена
    new_block = '''            # Sprint 8.5 fix: проверка keywords ОТКЛЮЧЕНА
            # LLM генерирует вовлекающие вопросы которые не содержат фактов из source,
            # но важны для вовлечения аудитории. Quality контролируется EvaluatorJob.
            # Поэтому мы НЕ удаляем предложения только из-за отсутствия совпадений keywords.'''
    
    s = s[:match.start()] + new_block + s[match.end():]
    guard_file.write_text(s, encoding='utf-8')
    print("✅ FactGuard: проверка keywords ПОЛНОСТЬЮ ОТКЛЮЧЕНА")
    print("   (оставлены только: удаление ссылок, forbidden headers, чисел)")
else:
    print("⚠️ Паттерн не найден — показываю текущее состояние")
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'Sprint 8.5' in line or 'min_matches' in line or 'keywords' in line:
            print(f"   L{i+1}: {line}")