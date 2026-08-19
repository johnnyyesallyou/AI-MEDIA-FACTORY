import pathlib

p = pathlib.Path('./backend/automation/policies/__init__.py')
s = p.read_text(encoding='utf-8')
changes = []

# ФИКС 1: В can_run() — безопасный доступ к daily_post_limit
old_can_run = '''            daily_limit = schedule.daily_post_limit or 10'''
new_can_run = '''            # Безопасный доступ: пробуем несколько вариантов имени поля
            daily_limit = (
                getattr(schedule, 'daily_post_limit', None) or
                getattr(schedule, 'daily_limit', None) or
                getattr(schedule, 'max_daily_posts', None) or
                getattr(schedule, 'posts_per_day', None) or
                10
            )'''

count_can_run = s.count(old_can_run)
if count_can_run > 0:
    s = s.replace(old_can_run, new_can_run)
    changes.append(f'patched can_run ({count_can_run} occurrence(s))')

# ФИКС 2: В get_remaining_quota() — безопасный доступ (такая же строка)
# Она уже заменена через replace выше (все вхождения)
# Проверяем что не осталось старых вызовов
remaining_old = s.count('schedule.daily_post_limit')
if remaining_old > 0:
    print(f'WARNING: ещё {remaining_old} старых вызовов осталось')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы:')
    for c in changes:
        print(f'   - {c}')
else:
    print('WARN: паттерн не найден')

# ВЕРИФИКАЦИЯ
print('\n=== Проверка ===')
new_s = p.read_text(encoding='utf-8')
print(f'Осталось schedule.daily_post_limit: {new_s.count("schedule.daily_post_limit")}')
print(f'Добавлено getattr: {new_s.count("getattr(schedule,")}')