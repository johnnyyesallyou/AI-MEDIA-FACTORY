import pathlib
import re
p = pathlib.Path('./frontend/src/components/Layout.tsx')
s = p.read_text(encoding='utf-8')
changes = []

# 1. Добавляем иконку Workflow в ЛЮБОЙ импорт lucide-react (работает и для однострочного, и для многострочного)
if 'Workflow' not in s and "} from 'lucide-react'" in s:
    s = s.replace("} from 'lucide-react'", ", Workflow } from 'lucide-react'", 1)
    changes.append('added Workflow icon import')

# 2. Добавляем пункт меню после /automation
if "'/workflows'" not in s:
    m = re.search(r"\{ path: '/automation',[^\n]*\},", s)
    if m:
        s = s[:m.end()] + "\n  { path: '/workflows', label: 'Workflows', icon: Workflow }," + s[m.end():]
        changes.append('added /workflows menu item')
    else:
        print('WARN: automation menu item not found')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: {", ".join(changes)}')
else:
    print('INFO: sidebar already patched')