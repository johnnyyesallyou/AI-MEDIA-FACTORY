import pathlib

p = pathlib.Path('./engines/writing/engine.py')
s = p.read_text(encoding='utf-8')

# Добавляем import os в начало файла (если его нет)
if 'import os' not in s:
    # Вставляем после первого import
    s = s.replace('import asyncio\n', 'import asyncio\nimport os\n', 1)
    print('OK: добавлен import os')

# Заменяем __init__ чтобы читать OLLAMA_URL из env
old_init = '''    def __init__(self, base_url: str = "http://localhost:11434", override_model: str = None):
        self.base_url = base_url'''

new_init = '''    def __init__(self, base_url: str = None, override_model: str = None):
        # Читаем OLLAMA_URL из env (как в EvaluatorEngine)
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")'''

if old_init in s:
    s = s.replace(old_init, new_init, 1)
    p.write_text(s, encoding='utf-8')
    print('OK: WritingEngine теперь читает OLLAMA_URL из env')
else:
    print('WARN: паттерн __init__ не найден')
    print('Ищем реальную сигнатуру __init__:')
    for i, line in enumerate(s.split('\n'), 1):
        if 'def __init__' in line and 'base_url' in line:
            print(f'  Line {i}: {line}')