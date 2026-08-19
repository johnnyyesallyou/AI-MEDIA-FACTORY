import pathlib, re
p = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = p.read_text(encoding='utf-8')
changes = []

# 1. Импорт ChannelManager
if "import ChannelManager" not in s:
    s = s.replace(
        "import { channelsAPI, automationAPI } from '../api/client';",
        "import { channelsAPI, automationAPI } from '../api/client';\nimport ChannelManager from '../components/ChannelManager';",
        1)
    changes.append('import ChannelManager')

# 2. State (если декларация отсутствует)
if 'const [showManagerModal' not in s:
    state_code = '\n  const [showManagerModal, setShowManagerModal] = useState(false);\n  const [managerChannel, setManagerChannel] = useState<{ id: string; name: string } | null>(null);'
    anchor = 'const [scheduleSaving, setScheduleSaving] = useState(false);'
    anchor2 = 'const [loading, setLoading] = useState(true);'
    if anchor in s:
        s = s.replace(anchor, anchor + state_code, 1)
        changes.append('state added')
    elif anchor2 in s:
        s = s.replace(anchor2, anchor2 + state_code, 1)
        changes.append('state added (fallback anchor)')
    else:
        print('WARN: anchor for state not found')

# 3. Определяем реальную функцию загрузки каналов из первого useEffect
m = re.search(r'useEffect\(\(\)\s*=>\s*\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', s)
loader = m.group(1) if m else None
print(f'   detected loader function: {loader}')

if 'onSaved={fetchChannels}' in s:
    repl = 'onSaved={' + loader + '}' if loader else 'onSaved={() => window.location.reload()}'
    s = s.replace('onSaved={fetchChannels}', repl, 1)
    changes.append('onSaved fixed -> ' + (loader or 'reload'))

# 4. Кнопка Settings (если ещё не добавлена)
if 'setShowManagerModal(true)' not in s:
    idx = s.find('<Trash2 size={18} />')
    if idx != -1:
        btn_start = s.rfind('<button', 0, idx)
        if btn_start != -1:
            btn = ('<button\n'
                   '                onClick={() => { setManagerChannel({ id: channel.id, name: channel.name }); setShowManagerModal(true); }}\n'
                   '                className="p-2 rounded-lg bg-purple-500 bg-opacity-20 text-purple-400 hover:bg-opacity-30 transition-colors"\n'
                   '                title="Настройки канала"\n'
                   '              >\n'
                   '                <Settings size={18} />\n'
                   '              </button>\n              ')
            s = s[:btn_start] + btn + s[btn_start:]
            changes.append('settings button added')
    else:
        print('WARN: Trash2 anchor not found')

if changes:
    p.write_text(s, encoding='utf-8')
    print('OK:')
    for c in changes:
        print(f'   ✅ {c}')
else:
    print('ℹ️ Всё уже на месте')