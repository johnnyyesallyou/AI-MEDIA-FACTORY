import pathlib, re
p = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = p.read_text(encoding='utf-8')
changes = []

# 1. Импорты (если нет)
if 'import ChannelManager' not in s:
    s = s.replace(
        "import { channelsAPI, automationAPI } from '../api/client';",
        "import { channelsAPI, automationAPI } from '../api/client';\nimport ChannelManager from '../components/ChannelManager';",
        1
    )
    changes.append('added ChannelManager import')

# 2. State: ищем ПОСЛЕДНИЙ useState в первой половине файла и добавляем после него
if 'const [showManagerModal' not in s:
    # Ищем все useState в первых 100 строках
    lines = s.split('\n')
    last_state_idx = -1
    for i, line in enumerate(lines[:100]):
        if 'useState' in line and 'const [' in line:
            last_state_idx = i
    
    if last_state_idx >= 0:
        # Вставляем после последнего useState
        state_code = [
            '  const [showManagerModal, setShowManagerModal] = useState(false);',
            '  const [managerChannel, setManagerChannel] = useState<{ id: string; name: string } | null>(null);'
        ]
        lines.insert(last_state_idx + 1, '\n'.join(state_code))
        s = '\n'.join(lines)
        changes.append(f'added manager state after line {last_state_idx + 1}')
    else:
        print('ERROR: no useState found')

# 3. Ищем функцию загрузки каналов
loader_match = re.search(r'const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*async', s)
if loader_match:
    loader = loader_match.group(1)
    print(f'   Found loader: {loader}')
    
    # Фиксим onSaved в ChannelManager
    if f'onSaved={{{loader}}}' not in s:
        s = re.sub(r'onSaved=\{[a-zA-Z_]+\}', f'onSaved={{{loader}}}', s)
        changes.append(f'fixed onSaved -> {loader}')
else:
    print('WARN: loader not found')

# 4. Кнопка Settings (если нет)
if 'setShowManagerModal(true)' not in s:
    idx = s.find('<Trash2 size={18} />')
    if idx != -1:
        btn_start = s.rfind('<button', 0, idx)
        if btn_start != -1:
            btn = '''<button
                onClick={() => { setManagerChannel({ id: channel.id, name: channel.name }); setShowManagerModal(true); }}
                className="p-2 rounded-lg bg-purple-500 bg-opacity-20 text-purple-400 hover:bg-opacity-30 transition-colors"
                title="Настройки канала"
              >
                <Settings size={18} />
              </button>
              '''
            s = s[:btn_start] + btn + s[btn_start:]
            changes.append('added Settings button')

# 5. Рендер ChannelManager (если нет)
modal_marker = '{showManagerModal && managerChannel && ('
if modal_marker not in s:
    loader = loader_match.group(1) if loader_match else 'loadChannels'
    modal_render = f'''
      {modal_marker}
        <ChannelManager
          channelId={{managerChannel.id}}
          channelName={{managerChannel.name}}
          onClose={{() => {{ setShowManagerModal(false); setManagerChannel(null); }}}}
          onSaved={{{loader}}}
        />
      )}}
'''
    export_idx = s.find('export default Channels;')
    if export_idx != -1:
        s = s[:export_idx] + modal_render + '\n' + s[export_idx:]
        changes.append('added ChannelManager render')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'✅ Применено {len(changes)} фиксов:')
    for c in changes:
        print(f'   - {c}')
else:
    print('ℹ️ Ничего не изменилось')