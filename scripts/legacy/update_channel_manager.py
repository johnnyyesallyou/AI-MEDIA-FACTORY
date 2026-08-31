import pathlib

f = pathlib.Path('./frontend/src/components/ChannelManager.tsx')
s = f.read_text(encoding='utf-8')
changes = []

# 1. Добавляем state для workflows
if 'const [workflows, setWorkflows]' not in s:
    # Ищем место после других state (например, после const [schedule, setSchedule])
    insert_marker = "const [adding, setAdding] = useState(false);"
    if insert_marker in s:
        workflows_state = '''

  // Workflows
  const [workflows, setWorkflows] = useState<{id: string; name: string}[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);
  const [savingWorkflow, setSavingWorkflow] = useState(false);'''
        s = s.replace(insert_marker, insert_marker + workflows_state, 1)
        changes.append("добавлены state: workflows, selectedWorkflowId, savingWorkflow")

# 2. Добавляем загрузку workflows в useEffect
if 'channelsAPI.listWorkflows' not in s:
    # Ищем useEffect который загружает данные
    if 'channelsAPI.getSchedule' in s:
        load_workflows = '''
    // Load workflows
    try {
      const wfData = await channelsAPI.listWorkflows();
      setWorkflows(wfData.workflows || []);
      console.log('Loaded workflows:', wfData.workflows);
    } catch (e) {
      console.error('Failed to load workflows:', e);
    }

'''
        # Вставляем после загрузки schedule
        s = s.replace(
            'channelsAPI.getSchedule(channelId)',
            load_workflows + '    channelsAPI.getSchedule(channelId)',
            1
        )
        changes.append("добавлена загрузка workflows из API")

# 3. Устанавливаем selectedWorkflowId из channel данных
if 'setSelectedWorkflowId' not in s or 'channelData.workflow_id' not in s:
    # Ищем где загружается channel
    if 'const channelData = await channelsAPI.get(channelId)' in s:
        set_selected = '''
      setSelectedWorkflowId(channelData.workflow_id || null);'''
        s = s.replace(
            'const channelData = await channelsAPI.get(channelId)',
            'const channelData = await channelsAPI.get(channelId)' + set_selected,
            1
        )
        changes.append("добавлено setSelectedWorkflowId из channelData")

# 4. Заменяем заглушку workflow на dropdown
old_workflow_tab = '''          {tab === 'workflow' && (
            <div className="space-y-4">
              <h3 className="text-white font-semibold">Workflow канала</h3>
              <div className="bg-slate-900 rounded-lg p-4 text-slate-300 text-sm">
                <p className="mb-2">Workflow определяет последовательность этапов обработки контента.</p>
                <p className="mb-4">Для редактирования откройте визуальный конструктор:</p>
                <a
                  href="/workflows"
                  className="inline-flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white rounded px-4 py-2"
                >
                  <Workflow size={16} /> Открыть Designer
                </a>
              </div>
              <div className="bg-yellow-900 bg-opacity-30 border border-yellow-700 rounded-lg p-4 text-yellow-200 text-sm">
                💡 Совет: привяжите workflow к каналу через раздел "Шаблоны" или через API.
              </div>
            </div>
          )}'''

new_workflow_tab = '''          {tab === 'workflow' && (
            <div className="space-y-4">
              <h3 className="text-white font-semibold">Workflow канала</h3>
              
              <div className="bg-slate-900 rounded-lg p-4">
                <label className="block text-slate-300 text-sm mb-2">
                  Выберите workflow для канала:
                </label>
                <select
                  value={selectedWorkflowId || ''}
                  onChange={(e) => setSelectedWorkflowId(e.target.value || null)}
                  disabled={savingWorkflow}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white"
                >
                  <option value="">— Не назначен (используется legacy fallback) —</option>
                  {workflows.map(wf => (
                    <option key={wf.id} value={wf.id}>
                      {wf.name} ({wf.id})
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={async () => {
                  setSavingWorkflow(true);
                  try {
                    await channelsAPI.update(channelId, { workflow_id: selectedWorkflowId });
                    onSaved();
                    alert('✅ Workflow успешно назначен!');
                  } catch (e) {
                    console.error('Failed to save workflow:', e);
                    alert('❌ Ошибка: ' + (e as Error).message);
                  } finally {
                    setSavingWorkflow(false);
                  }
                }}
                disabled={savingWorkflow}
                className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 text-white rounded px-4 py-2 font-medium"
              >
                {savingWorkflow ? 'Сохранение...' : '💾 Сохранить workflow'}
              </button>

              <div className="bg-slate-900 rounded-lg p-4 text-slate-400 text-sm">
                <p className="mb-2">💡 <strong>Workflow</strong> определяет последовательность этапов:</p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li><code>wf-simple</code>: research → writing → evaluation → publish</li>
                  <li><code>wf-default-full</code>: research → decision → writing → evaluation → revision → re_evaluation → publish</li>
                  <li><code>wf-research-only</code>: только research (без публикации)</li>
                </ul>
              </div>

              <a
                href="/workflows"
                className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 text-sm"
              >
                <Workflow size={14} /> Открыть визуальный Designer
              </a>
            </div>
          )}'''

if old_workflow_tab in s:
    s = s.replace(old_workflow_tab, new_workflow_tab, 1)
    changes.append("вкладка workflow переписана: dropdown + кнопка сохранения")
else:
    print("⚠️ Точный паттерн workflow tab не найден")
    print("   Показываю текущее состояние:")
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if "tab === 'workflow'" in line:
            for j in range(i, min(i+20, len(lines))):
                print(f"   {j+1}: {lines[j]}")
            break

if changes:
    f.write_text(s, encoding='utf-8')
    print(f"✅ Применено {len(changes)} изменений:")
    for c in changes:
        print(f"   - {c}")
else:
    print("⚠️ Изменения не применены")