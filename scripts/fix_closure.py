import pathlib
p = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = p.read_text(encoding='utf-8')
changed = []
if 'const loadAllSchedules = async () => {' in s:
    s = s.replace('const loadAllSchedules = async () => {', 'const loadAllSchedules = async (chs: any[]) => {'); changed.append('sig')
if 'for (const channel of channels) {' in s:
    s = s.replace('for (const channel of channels) {', 'for (const channel of chs) {'); changed.append('loop')
if 'setTimeout(() => loadAllSchedules(), 500);' in s:
    s = s.replace('setTimeout(() => loadAllSchedules(), 500);', 'setTimeout(() => loadAllSchedules(response.data.channels || []), 500);'); changed.append('call')
if changed:
    p.write_text(s, encoding='utf-8')
    print('OK: closure fixed ->', ', '.join(changed))
else:
    print('nothing to fix')