import pathlib
p = pathlib.Path('./frontend/src/App.tsx')
s = p.read_text(encoding='utf-8')
changes = []

# 1. Добавляем импорт Workflows
if 'import Workflows' not in s:
    s = s.replace(
        "import Sandbox from './pages/Sandbox';",
        "import Sandbox from './pages/Sandbox';\nimport Workflows from './pages/Workflows';"
    )
    changes.append('added Workflows import')

# 2. Добавляем роут /workflows (после /automation)
if 'path="workflows"' not in s:
    s = s.replace(
        '<Route path="automation" element={<Automation />} />',
        '<Route path="automation" element={<Automation />} />\n          <Route path="workflows" element={<Workflows />} />'
    )
    changes.append('added /workflows route')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'✅ Применено: {", ".join(changes)}')
else:
    print('ℹ️ Ничего не изменилось')