import pathlib
import re

p = pathlib.Path('./frontend/src/components/Layout.tsx')
s = p.read_text(encoding='utf-8')
changes = []

# 1. Добавляем импорт иконки Workflow
if 'Workflow' not in s and 'GitBranch' not in s:
    import_match = s.find("from 'lucide-react'")
    if import_match > 0:
        line_start = s.rfind('\n', 0, import_match) + 1
        line_end = s.find('\n', import_match)
        import_line = s[line_start:line_end]
        
        if import_line.endswith(';'):
            new_import = import_line.replace('}', ', Workflow }')
        else:
            new_import = import_line.replace('}', ', Workflow }')
        
        s = s[:line_start] + new_import + s[line_end:]
        changes.append('added Workflow icon import')

# 2. Добавляем пункт меню после /automation
if "'/workflows'" not in s:
    automation_pattern = r"(\{ path: '/automation', label: 'Automation', icon: \w+ \},)"
    replacement = r"\1\n  { path: '/workflows', label: 'Workflows', icon: Workflow },"
    
    s_new, count = re.subn(automation_pattern, replacement, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added /workflows menu item after /automation')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'✅ Применено {len(changes)} фиксов:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Workflows уже добавлен в sidebar')