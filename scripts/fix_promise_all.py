import pathlib

f = pathlib.Path('./frontend/src/components/ChannelManager.tsx')
s = f.read_text(encoding='utf-8')

# Ищем сломанный блок
broken_pattern = '''      const [srcRes, schRes] = await Promise.all([
        channelsAPI.listSources(channelId),

    // Load workflows
    try {
      const wfData = await channelsAPI.listWorkflows();
      setWorkflows(wfData.workflows || []);
      console.log('Loaded workflows:', wfData.workflows);
    } catch (e) {
      console.error('Failed to load workflows:', e);
    }

    channelsAPI.getSchedule(channelId).catch(() => null),
      ]);'''

fixed_code = '''      // Load workflows separately
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

if broken_pattern in s:
    s = s.replace(broken_pattern, fixed_code, 1)
    print("✅ Promise.all исправлен (workflows загружается отдельно)")
    
    # Добавляем импорт workflowsAPI
    if 'workflowsAPI' not in s:
        s = s.replace(
            "import { channelsAPI } from '../api/client';",
            "import { channelsAPI, workflowsAPI } from '../api/client';",
            1
        )
        print("✅ Добавлен импорт workflowsAPI")
    
    f.write_text(s, encoding='utf-8')
else:
    print("⚠️ Сломанный паттерн не найден — показываю problem area:")
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'Promise.all([' in line:
            for j in range(i, min(i+20, len(lines))):
                print(f"   {j+1}: {lines[j]}")
            break