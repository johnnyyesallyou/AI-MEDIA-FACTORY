import pathlib

p = pathlib.Path("/app/backend/automation/runtime/job_adapters.py")
c = p.read_text(encoding="utf-8")

# Проверяем есть ли _maybe_await
if "_maybe_await" in c:
    # Ищем где он вызывается
    import re
    matches = re.findall(r'await _maybe_await\([^)]+\)', c)
    print(f"[i] _maybe_await already exists, {len(matches)} calls found")
    
    # Проверяем импорты
    if "import inspect" not in c:
        c = "import inspect\n" + c
        print("[OK] Added import inspect")
    
    p.write_text(c, encoding="utf-8")
else:
    # Добавляем _maybe_await helper
    helper = '''
import inspect
import logging

logger = logging.getLogger(__name__)


async def _maybe_await(result):
    """Helper для вызова async/sync функций.
    
    Если result - coroutine, await его.
    Иначе вернуть как есть.
    """
    if inspect.iscoroutine(result) or inspect.isawaitable(result):
        return await result
    return result

'''
    # Вставляем после импортов
    lines = c.split('\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            insert_idx = i + 1
    
    lines.insert(insert_idx, helper)
    c = '\n'.join(lines)
    p.write_text(c, encoding="utf-8")
    print("[OK] _maybe_await helper added")