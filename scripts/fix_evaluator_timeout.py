import pathlib, py_compile

p = pathlib.Path('./engines/evaluator/engine.py')
s = p.read_text(encoding='utf-8')

# Проверяем есть ли уже retry
if 'max_retries' in s or 'for attempt in' in s:
    print("ℹ️ EvaluatorEngine уже имеет retry-логику — пропускаем")
else:
    # Добавляем import time если нет
    if 'import time' not in s:
        s = s.replace('import requests', 'import requests\nimport time', 1)
    
    # Ищем requests.post(...timeout=...) и увеличиваем timeout
    import re
    pattern = r'requests\.post\(([^)]*?)timeout=(\d+)([^)]*?)\)'
    
    def increase_timeout(match):
        before = match.group(1)
        old_timeout = match.group(2)
        after = match.group(3)
        new_timeout = '300'
        print(f"   timeout {old_timeout} → {new_timeout}")
        return f'requests.post({before}timeout={new_timeout}{after})'
    
    s_new, count = re.subn(pattern, increase_timeout, s)
    
    if count > 0:
        p.write_text(s_new, encoding='utf-8')
        print(f"✅ EvaluatorEngine: увеличен timeout в {count} местах")
    else:
        print("⚠️ Паттерн timeout не найден в EvaluatorEngine")

# Проверяем синтаксис
try:
    py_compile.compile(str(p), doraise=True)
    print("✅ Синтаксис валиден")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")