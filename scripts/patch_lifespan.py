import pathlib

p = pathlib.Path("/app/main.py")
c = p.read_text(encoding="utf-8")

# Ищем строку с print("🚀 AI Media Factory Dashboard starting...")
old = '    print("🚀 AI Media Factory Dashboard starting...", flush=True)'
new = '''    print("🚀 AI Media Factory Dashboard starting...", flush=True)
    
    # Sprint 48: Явный вызов регистрации jobs (module-level может не сработать)
    register_all_jobs()'''

if old in c and "register_all_jobs()" not in c.split(old)[1].split('\n')[1] if old in c else False:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] Добавлен явный вызов register_all_jobs() в lifespan")
else:
    print("[i] Уже добавлено или паттерн не найден")