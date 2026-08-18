import pathlib

f = pathlib.Path('./frontend/src/components/ChannelManager.tsx')
lines = f.read_text(encoding='utf-8').split('\n')

# Заменяем строки 67-80 (0-indexed: 66-79) на правильный код
new_code = '''      // Load workflows separately (not in Promise.all)
      try {
        const wfData = await workflowsAPI.list();
        setWorkflows(wfData.data || []);
        console.log('Loaded workflows:', wfData.data);
      } catch (e) {
        console.error('Failed to load workflows:', e);
      }

      const [srcRes, schRes] = await Promise.all([
        channelsAPI.listSources(channelId),
        channelsAPI.getSchedule(channelId).catch(() => null),
      ]);'''

# Удаляем строки 67-80 (14 строк)
del lines[66:80]

# Вставляем новый код на место строки 67
lines.insert(66, new_code)

f.write_text('\n'.join(lines), encoding='utf-8')
print("✅ Строки 67-80 заменены на правильный код")