import React, { useEffect, useState } from 'react';
import { X, Plus, Trash2, Save, Clock, Rss, Workflow } from 'lucide-react';
import { channelsAPI, workflowsAPI } from '../api/client';

interface Source {
  id: string;
  name: string;
  source_type: string;
  url: string;
  priority: number;
  is_active?: boolean;
}

interface Schedule {
  cron_expression: string;
  timezone: string;
  max_posts_per_day: number;
  auto_publish: boolean;
  is_active: boolean;
}


interface ChannelManagerProps {
  channelId: string;
  channelName: string;
  onClose: () => void;
  onSaved: () => void;
}

const CRON_PRESETS = [
  { label: 'Каждые 2 часа', value: '0 */2 * * *' },
  { label: 'Каждые 3 часа', value: '0 */3 * * *' },
  { label: 'Каждые 4 часа', value: '0 */4 * * *' },
  { label: '3 раза в день', value: '0 9,15,21 * * *' },
  { label: 'Утро и вечер', value: '0 9,18 * * *' },
  { label: 'Раз в день', value: '0 10 * * *' },
];

export default function ChannelManager({ channelId, channelName, onClose, onSaved }: ChannelManagerProps) {
  const [tab, setTab] = useState<'sources' | 'schedule' | 'workflow'>('sources');
  const [loading, setLoading] = useState(true);

  // Sources
  const [sources, setSources] = useState<Source[]>([]);
  const [newSource, setNewSource] = useState({ name: '', url: '', priority: 3, source_type: 'rss' });
  const [adding, setAdding] = useState(false);

  // Workflows
  const [workflows, setWorkflows] = useState<{id: string; name: string}[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);
  const [savingWorkflow, setSavingWorkflow] = useState(false);

  // Schedule
  const [schedule, setSchedule] = useState<Schedule>({
    cron_expression: '0 */3 * * *',
    timezone: 'Europe/Moscow',
    max_posts_per_day: 10,
    auto_publish: true,
    is_active: true,
  });

  useEffect(() => { loadAll(); }, [channelId]);

  const loadAll = async () => {
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
  };

  const addSource = async () => {
    if (!newSource.name || !newSource.url) return;
    setAdding(true);
    try {
      const id = `src-${Date.now()}`;
      await channelsAPI.addSource(channelId, { ...newSource, id });
      setNewSource({ name: '', url: '', priority: 3, source_type: 'rss' });
      await loadAll();
      onSaved();
    } finally {
      setAdding(false);
    }
  };

  const deleteSource = async (sourceId: string) => {
    if (!confirm('Удалить источник?')) return;
    await channelsAPI.deleteSource(channelId, sourceId);
    await loadAll();
    onSaved();
  };

  const saveSchedule = async () => {
    await channelsAPI.updateSchedule(channelId, schedule);
    alert('Расписание сохранено!');
    onSaved();
  };

  const nextRunPreview = () => {
    // Простое превью cron (только для отображения)
    const preset = CRON_PRESETS.find(p => p.value === schedule.cron_expression);
    return preset ? preset.label : schedule.cron_expression;
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-slate-800 rounded-lg p-8 text-white">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-lg w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700">
          <h2 className="text-xl font-bold text-white">⚙️ Менеджер: {channelName}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X size={24} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-700">
          <button
            onClick={() => setTab('sources')}
            className={`flex-1 py-3 px-4 font-medium flex items-center justify-center gap-2 ${tab === 'sources' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-slate-400'}`}
          >
            <Rss size={18} /> Источники ({sources.length})
          </button>
          <button
            onClick={() => setTab('schedule')}
            className={`flex-1 py-3 px-4 font-medium flex items-center justify-center gap-2 ${tab === 'schedule' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-slate-400'}`}
          >
            <Clock size={18} /> Расписание
          </button>
          <button
            onClick={() => setTab('workflow')}
            className={`flex-1 py-3 px-4 font-medium flex items-center justify-center gap-2 ${tab === 'workflow' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-slate-400'}`}
          >
            <Workflow size={18} /> Workflow
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {tab === 'sources' && (
            <div>
              <h3 className="text-white font-semibold mb-4">Источники RSS</h3>

              {sources.length === 0 && (
                <div className="text-slate-400 text-center py-8 bg-slate-900 rounded-lg">
                  Источники не добавлены
                </div>
              )}

              <div className="space-y-2 mb-6">
                {sources.map(s => (
                  <div key={s.id} className="flex items-center gap-3 bg-slate-900 rounded-lg p-3">
                    <Rss size={16} className="text-blue-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-white font-medium truncate">{s.name}</div>
                      <div className="text-slate-400 text-xs truncate">{s.url}</div>
                    </div>
                    <span className="text-xs px-2 py-1 bg-blue-500 bg-opacity-20 text-blue-400 rounded">
                      P{s.priority}
                    </span>
                    <button
                      onClick={() => deleteSource(s.id)}
                      className="text-red-400 hover:text-red-300 p-1"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>

              <div className="border-t border-slate-700 pt-4">
                <h4 className="text-white font-medium mb-3 flex items-center gap-2">
                  <Plus size={16} /> Добавить источник
                </h4>
                <div className="grid grid-cols-2 gap-3 mb-3">
                  <input
                    type="text"
                    placeholder="Название (например, Habr AI)"
                    value={newSource.name}
                    onChange={e => setNewSource({ ...newSource, name: e.target.value })}
                    className="bg-slate-900 text-white rounded px-3 py-2 text-sm"
                  />
                  <input
                    type="text"
                    placeholder="RSS URL"
                    value={newSource.url}
                    onChange={e => setNewSource({ ...newSource, url: e.target.value })}
                    className="bg-slate-900 text-white rounded px-3 py-2 text-sm"
                  />
                </div>
                <div className="flex items-center gap-3">
                  <select
                    value={newSource.priority}
                    onChange={e => setNewSource({ ...newSource, priority: Number(e.target.value) })}
                    className="bg-slate-900 text-white rounded px-3 py-2 text-sm"
                  >
                    <option value={1}>Приоритет 1 (низкий)</option>
                    <option value={2}>Приоритет 2</option>
                    <option value={3}>Приоритет 3 (средний)</option>
                    <option value={4}>Приоритет 4</option>
                    <option value={5}>Приоритет 5 (высокий)</option>
                  </select>
                  <button
                    onClick={addSource}
                    disabled={adding || !newSource.name || !newSource.url}
                    className="bg-blue-500 hover:bg-blue-600 disabled:bg-slate-600 text-white rounded px-4 py-2 text-sm font-medium"
                  >
                    {adding ? 'Добавление...' : '+ Добавить'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {tab === 'schedule' && (
            <div className="space-y-4">
              <h3 className="text-white font-semibold">Расписание публикаций</h3>

              <div>
                <label className="text-slate-300 text-sm mb-2 block">Пресеты:</label>
                <div className="grid grid-cols-2 gap-2 mb-3">
                  {CRON_PRESETS.map(p => (
                    <button
                      key={p.value}
                      onClick={() => setSchedule({ ...schedule, cron_expression: p.value })}
                      className={`text-left px-3 py-2 rounded text-sm ${schedule.cron_expression === p.value ? 'bg-blue-500 text-white' : 'bg-slate-900 text-slate-300 hover:bg-slate-700'}`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-slate-300 text-sm mb-2 block">Custom cron:</label>
                <input
                  type="text"
                  value={schedule.cron_expression}
                  onChange={e => setSchedule({ ...schedule, cron_expression: e.target.value })}
                  className="w-full bg-slate-900 text-white rounded px-3 py-2 font-mono text-sm"
                />
                <div className="text-slate-400 text-xs mt-1">Текущий: {nextRunPreview()}</div>
              </div>

              <div>
                <label className="text-slate-300 text-sm mb-2 block">Лимит постов в день:</label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={schedule.max_posts_per_day}
                  onChange={e => setSchedule({ ...schedule, max_posts_per_day: Number(e.target.value) })}
                  className="w-full bg-slate-900 text-white rounded px-3 py-2"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="auto_publish"
                  checked={schedule.auto_publish}
                  onChange={e => setSchedule({ ...schedule, auto_publish: e.target.checked })}
                  className="w-4 h-4"
                />
                <label htmlFor="auto_publish" className="text-white text-sm">
                  Автоматически публиковать одобренные посты
                </label>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={schedule.is_active}
                  onChange={e => setSchedule({ ...schedule, is_active: e.target.checked })}
                  className="w-4 h-4"
                />
                <label htmlFor="is_active" className="text-white text-sm">
                  Расписание активно
                </label>
              </div>

              <button
                onClick={saveSchedule}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white rounded px-4 py-3 font-medium flex items-center justify-center gap-2"
              >
                <Save size={18} /> Сохранить расписание
              </button>
            </div>
          )}

          {tab === 'workflow' && (
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
          )}
        </div>
      </div>
    </div>
  );
}