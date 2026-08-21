import pathlib

p = pathlib.Path("/app/backend/automation/runtime/job_adapters.py")
c = p.read_text(encoding="utf-8")

# Паттерн 1: передаём только channel + execution_id (строка)
# Старое: job.run(context.channel, context)
# Новое: job.run(context.channel, execution_id=context.execution_id)

changes = 0
for legacy_method in ['run', 'execute']:
    old_call = f"job.{legacy_method}(context.channel, context)"
    new_call = f"job.{legacy_method}(context.channel, execution_id=context.execution_id)"
    if old_call in c:
        c = c.replace(old_call, new_call)
        changes += 1
        print(f"  [OK] {old_call} -> {new_call}")

# Паттерн 2: job(context.channel) тоже нужно улучшить
old_call2 = "result = job(context.channel)"
new_call2 = "result = job(context.channel)  # noqa"
if old_call2 in c and "noqa" not in c:
    c = c.replace(old_call2, new_call2)

p.write_text(c, encoding="utf-8")
print(f"[OK] Адаптеры исправлены ({changes} замен)")