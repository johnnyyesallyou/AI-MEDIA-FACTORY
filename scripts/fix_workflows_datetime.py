import pathlib

f = pathlib.Path('./backend/app/api/v1/workflows.py')
s = f.read_text(encoding='utf-8')

# Старая версия (проблемная)
old_to_response = '''def _to_response(item) -> WorkflowResponse:
    return WorkflowResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        definition=item.definition,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )'''

# Новая версия с обработкой None
new_to_response = '''def _to_response(item) -> WorkflowResponse:
    from datetime import datetime
    return WorkflowResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        definition=item.definition,
        is_active=item.is_active,
        created_at=item.created_at or datetime.utcnow(),
        updated_at=item.updated_at or datetime.utcnow(),
    )'''

if old_to_response in s:
    s = s.replace(old_to_response, new_to_response, 1)
    f.write_text(s, encoding='utf-8')
    print("✅ _to_response исправлен — обрабатывает NULL datetime")
else:
    print("⚠️ Паттерн не найден — показываю текущий код:")
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if '_to_response' in line and 'def ' in line:
            for j in range(i, min(i+15, len(lines))):
                print(f"   {j+1}: {lines[j]}")
            break

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ Синтаксис валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")