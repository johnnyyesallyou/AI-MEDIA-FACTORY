import pathlib, re

f = pathlib.Path('./frontend/src/components/ChannelManager.tsx')
s = f.read_text(encoding='utf-8')

# Находим функцию loadAll (от "const loadAll" до закрывающей };)
# Используем regex для замены всей функции
new_loadAll = '''  const loadAll = async () => {
    setLoading(true);
    try {
      // 1. Load workflows separately (not in Promise.all)
      try {
        const wfData = await workflowsAPI.list();
        setWorkflows(wfData.data || []);
        console.log('Loaded workflows:', wfData.data);
      } catch (e) {
        console.error('Failed to load workflows:', e);
      }

      // 2. Load channel info to get workflow_id
      try {
        const channelData = await channelsAPI.get(channelId);
        setSelectedWorkflowId(channelData.data.workflow_id || null);
      } catch (e) {
        console.error('Failed to load channel:', e);
      }

      // 3. Load sources and schedule in parallel
      const [srcRes, schRes] = await Promise.all([
        channelsAPI.listSources(channelId),
        channelsAPI.getSchedule(channelId).catch(() => null),
      ]);
      
      setSources(srcRes.data || []);
      if (schRes?.data) setSchedule(schRes.data);
    } catch (e) {
      console.error('LoadAll error:', e);
    } finally {
      setLoading(false);
    }
  };'''

# Ищем старую функцию (от "const loadAll" до следующей функции "const addSource")
pattern = r'  const loadAll = async \(\) => \{.*?\n  \};\n\n  const addSource'
match = re.search(pattern, s, re.DOTALL)

if match:
    s = s[:match.start()] + new_loadAll + '\n\n  const addSource' + s[match.end():]
    print("✅ Функция loadAll переписана начисто")
    f.write_text(s, encoding='utf-8')
else:
    print("⚠️ Функция loadAll не найдена — попробуем другой подход")
    
    # Альтернативный подход: построчно
    lines = s.split('\n')
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if 'const loadAll = async () =>' in line:
            start_idx = i
        if start_idx is not None and i > start_idx + 5:
            # Ищем закрывающую }; функции (на уровне отступа 2)
            if line.strip() == '};' and lines[i-1].strip() == '}':
                end_idx = i
                break
    
    if start_idx is not None and end_idx is not None:
        print(f"   Найдена функция на строках {start_idx+1}-{end_idx+1}")
        new_lines = lines[:start_idx] + new_loadAll.split('\n') + lines[end_idx+1:]
        f.write_text('\n'.join(new_lines), encoding='utf-8')
        print("✅ Функция loadAll переписана")
    else:
        print("❌ Не удалось найти функцию")