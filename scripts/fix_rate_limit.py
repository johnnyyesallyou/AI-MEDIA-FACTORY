import pathlib, re

p = pathlib.Path('./backend/automation/policies/__init__.py')
s = p.read_text(encoding='utf-8')
changes = []

# Ищем блок где читается daily_limit
# Текущий код:
# daily_limit = (
#     getattr(schedule, 'daily_post_limit', None) or
#     getattr(schedule, 'max_posts_per_day', None) or
#     10
# )

old_pattern = r'''daily_limit = \(\s*getattr\(schedule, 'daily_post_limit', None\) or\s*getattr\(schedule, 'max_posts_per_day', None\) or\s*10\s*\)'''

new_code = '''daily_limit = (
                getattr(schedule, 'max_posts_per_day', None) or
                getattr(schedule, 'daily_post_limit', None) or
                50  # Increased default from 10 to 50
            )'''

s_new, count = re.subn(old_pattern, new_code, s, flags=re.DOTALL)

if count > 0:
    s = s_new
    changes.append("RateLimitPolicy теперь читает max_posts_per_day ПЕРВЫМ")
    changes.append("Default увеличен с 10 до 50")
else:
    # Альтернативный паттерн: ищем оба getattr
    if "getattr(schedule, 'daily_post_limit', None)" in s:
        # Меняем порядок: max_posts_per_day должен быть ПЕРВЫМ
        s = s.replace(
            "getattr(schedule, 'daily_post_limit', None) or",
            "getattr(schedule, 'max_posts_per_day', None) or",
            1
        )
        s = s.replace(
            "getattr(schedule, 'max_posts_per_day', None) or",
            "getattr(schedule, 'daily_post_limit', None) or",
            2
        )
        # Меняем default с 10 на 50
        s = s.replace("or\n                10\n            )", "or\n                50\n            )")
        changes.append("RateLimitPolicy исправлен (альтернативный метод)")

if changes:
    p.write_text(s, encoding='utf-8')
    print(f"✅ Применено {len(changes)} фиксов:")
    for c in changes:
        print(f"   - {c}")
else:
    print("⚠️ Паттерн не найден")
    # Показываем текущий код
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'daily_limit' in line:
            print(f"   L{i+1}: {line}")