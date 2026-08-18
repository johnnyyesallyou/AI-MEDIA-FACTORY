import pathlib
p = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = p.read_text(encoding='utf-8')
changes = []

# 1. Добавляем импорт
if 'ChannelManager' not in s:
    s = s.replace(
        "import { Plus, Radio, Globe, Type, Settings, Trash2, Edit2, MessageCircle, CheckCircle, XCircle, Clock } from 'lucide-react';",
        "import { Plus, Radio, Globe, Type, Settings, Trash2, Edit2, MessageCircle, CheckCircle, XCircle, Clock } from 'lucide-react';\nimport ChannelManager from '../components/ChannelManager';",
        1
    )
    changes.append('added ChannelManager import')

# 2. Добавляем state для модалки
if 'showManagerModal' not in s:
    s = s.replace(
        'const [scheduleSaving, setScheduleSaving] = useState(false);',
        'const [scheduleSaving, setScheduleSaving] = useState(false);\n  const [showManagerModal, setShowManagerModal] = useState(false);\n  const [managerChannel, setManagerChannel] = useState<{id: string, name: string} | null>(null);',
        1
    )
    changes.append('added manager state')

# 3. Добавляем кнопку ⚙️ рядом с существующими кнопками карточки
# Ищем блок с кнопкой Schedule (Clock) и вставляем Settings перед ней
if 'onClick={() => openScheduleModal' in s and 'openManager' not in s:
    # Ищем паттерн с Clock кнопкой и вставляем Settings перед ней
    import re
    pattern = r'(<button[^>]*onClick=\{\(\) => openScheduleModal[^}]*\}[^>]*>\s*<Clock)'
    replacement = '''<button
                onClick={() => { setManagerChannel({id: channel.id, name: channel.name}); setShowManagerModal(true); }}
                className="p-2 rounded-lg bg-purple-500 bg-opacity-20 text-purple-400 hover:bg-opacity-30 transition-colors"
                title="Настройки канала"
              >
                <Settings size={18} />
              </button>
              \\1'''
    s_new, count = re.subn(pattern, replacement, s, count=1)
    if count > 0:
        s = s_new
        changes.append('added Settings button to channel card')

# 4. Добавляем рендер модалки в самом конце компонента (перед закрывающим </div>)
if 'showManagerModal && managerChannel' not in s:
    modal_render = '''
      {showManagerModal && managerChannel && (
        <ChannelManager
          channelId={managerChannel.id}
          channelName={managerChannel.name}
          onClose={() => { setShowManagerModal(false); setManagerChannel(null); }}
          onSaved={fetchChannels}
        />
      )}
'''
    # Вставляем перед export default
    s = s.replace('export default Channels;', modal_render + '\nexport default Channels;')
    changes.append('added ChannelManager render')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'✅ Применено {len(changes)} фиксов:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Ничего не изменилось')