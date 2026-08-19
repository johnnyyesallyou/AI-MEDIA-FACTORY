import pathlib, re
p = pathlib.Path('./frontend/src/components/ChannelManager.tsx')
s = p.read_text(encoding='utf-8')
changes = []

old_imp = "import { X, Plus, Trash2, Save, Clock, Rss, Workflow, CheckCircle, AlertCircle } from 'lucide-react';"
new_imp = "import { X, Plus, Trash2, Save, Clock, Rss, Workflow } from 'lucide-react';"
if old_imp in s:
    s = s.replace(old_imp, new_imp, 1)
    changes.append('removed unused lucide imports')

# Удаляем неиспользуемый интерфейс Channel
s2 = re.sub(r'interface Channel \{[^}]*\}\n', '', s, count=1, flags=re.DOTALL)
if s2 != s:
    s = s2
    changes.append('removed unused Channel interface')

if changes:
    p.write_text(s, encoding='utf-8')
    print('OK:')
    for c in changes:
        print(f'   ✅ {c}')
else:
    print('ℹ️ Уже чисто')