import pathlib

f = pathlib.Path('./frontend/src/components/ChannelManager.tsx')
s = f.read_text(encoding='utf-8')

# 1. Добавляем импорт workflowsAPI (если ещё нет)
if 'workflowsAPI' not in s:
    s = s.replace(
        "import { channelsAPI } from '../api/client';",
        "import { channelsAPI, workflowsAPI } from '../api/client';",
        1
    )
    print("✅ Добавлен импорт workflowsAPI")

# 2. Точный сломанный блок (из вывода пользователя)
broken_block = '''      const [srcRes, schRes] = await Promise.all([
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

fixed_block = '''      // Load workflows separately (not in Promise.all)
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

if broken_block in s:
    s = s.replace(broken_block, fixed_block, 1)
    print("✅ Promise.all исправлен (workflows загружается отдельно)")
    f.write_text(s, encoding='utf-8')
else:
    print("⚠️ Точный паттерн не совпал — попробуем построчно")
    
    # Альтернативный подход: удаляем строки построчно
    lines = s.split('\n')
    new_lines = []
    skip = False
    removed_count = 0
    
    for i, line in enumerate(lines):
        # Начинаем пропуск когда видим "// Load workflows" ВНУТРИ Promise.all
        if '// Load workflows' in line and i > 60 and i < 80:
            # Проверяем что это внутри Promise.all (предыдущие строки содержат Promise.all)
            if any('Promise.all' in lines[j] for j in range(max(0, i-5), i)):
                skip = True
                removed_count += 1
                # Вставляем ПЕРЕД Promise.all правильную загрузку
                indent = '      '
                new_lines.append(indent + '// Load workflows separately')
                new_lines.append(indent + 'try {')
                new_lines.append(indent + '  const wfData = await workflowsAPI.list();')
                new_lines.append(indent + '  setWorkflows(wfData.data || []);')
                new_lines.append(indent + '  console.log("Loaded workflows:", wfData.data);')
                new_lines.append(indent + '} catch (e) {')
                new_lines.append(indent + '  console.error("Failed to load workflows:", e);')
                new_lines.append(indent + '}')
                new_lines.append('')
                continue
        
        # Заканчиваем пропуск на строке с "]);"
        if skip and ']);' in line:
            skip = False
            new_lines.append(line)
            continue
        
        # Пропускаем строки внутри сломанного блока
        if skip:
            removed_count += 1
            continue
        
        new_lines.append(line)
    
    if removed_count > 0:
        s = '\n'.join(new_lines)
        f.write_text(s, encoding='utf-8')
        print(f"✅ Удалено {removed_count} строк, вставлена правильная загрузка")
    else:
        print("❌ Ничего не исправлено")

# 3. Добавляем setSelectedWorkflowId (если нет)
if 'setSelectedWorkflowId(channelData.workflow_id' not in s:
    # Ищем где загружается channelData
    if 'const channelData = await channelsAPI.get(channelId);' in s:
        s = s.replace(
            'const channelData = await channelsAPI.get(channelId);',
            'const channelData = await channelsAPI.get(channelId);\n      setSelectedWorkflowId(channelData.workflow_id || null);',
            1
        )
        print("✅ Добавлено setSelectedWorkflowId")

print("\n✅ Файл сохранён")