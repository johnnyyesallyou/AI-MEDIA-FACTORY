import React, { useEffect, useState, useCallback } from 'react';
import { pipelineMetricsAPI } from '../api/client';
import {
  Activity, AlertTriangle, CheckCircle2, Clock, Zap,
  RefreshCw, Gauge, Coins, Send, Timer
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts';

interface ChannelHealth {
  channel_id: string;
  channel_name: string;
  status: 'healthy' | 'warning' | 'critical';
  runs: number;
  success_rate: number;
  topics_published: number;
  errors_count: number;
  total_ms: { avg: number; p50: number; p95: number };
  llm: {
    llm_calls: number; llm_errors: number; llm_avg_latency_ms: number;
    tokens_in: number; tokens_out: number; llm_model: string | null;
  };
  last_run_at: string | null;
}

interface Alert {
  type: string;
  severity: 'critical' | 'warning' | 'info';
  channel_id: string;
  channel_name: string;
  message: string;
  execution_id: string | null;
  created_at: string | null;
}

interface TrendPoint {
  hour: string;
  runs: number;
  published: number;
  errors: number;
  avg_total_ms: number;
  avg_llm_latency_ms: number;
}

interface RunMetrics {
  id: string;
  channel_id: string;
  execution_id: string | null;
  stage_timings_ms: { research: number; writing: number; media: number; publishing: number };
  total_ms: number;
  topics: { found: number; generated: number; published: number };
  errors_count: number;
  success: boolean;
  llm: {
    llm_calls: number; llm_errors: number; llm_latency_ms: number;
    tokens_in: number; tokens_out: number; llm_model: string | null;
  };
  created_at: string | null;
}

const statusColor = (s: string) =>
  s === 'healthy' ? 'text-green-400' : s === 'warning' ? 'text-yellow-400' : 'text-red-400';

const statusBg = (s: string) =>
  s === 'healthy' ? 'bg-green-500/10 border-green-500/30'
    : s === 'warning' ? 'bg-yellow-500/10 border-yellow-500/30'
    : 'bg-red-500/10 border-red-500/30';

const severityIcon = (sev: string) =>
  sev === 'critical'
    ? <AlertTriangle size={16} className="text-red-400 shrink-0" />
    : <AlertTriangle size={16} className="text-yellow-400 shrink-0" />;

const sec = (ms: number) => (ms / 1000).toFixed(1);

const KpiCard: React.FC<{ icon: React.ReactNode; label: string; value: string; sub?: string }> = ({ icon, label, value, sub }) => (
  <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
    <div className="flex items-center gap-2 text-gray-400 text-sm">
      {icon}<span>{label}</span>
    </div>
    <div className="text-2xl font-bold text-white mt-1">{value}</div>
    {sub && <div className="text-xs text-gray-500 mt-1">{sub}</div>}
  </div>
);

const PipelineDashboard: React.FC = () => {
  const [health, setHealth] = useState<ChannelHealth[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<string | null>(null);
  const [runs, setRuns] = useState<RunMetrics[]>([]);
  const [windowHours, setWindowHours] = useState(24);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAll = useCallback(async () => {
    try {
      const [h, a, t] = await Promise.all([
        pipelineMetricsAPI.healthOverview(windowHours),
        pipelineMetricsAPI.alerts(windowHours),
        pipelineMetricsAPI.trends(windowHours),
      ]);
      setHealth(h.data.channels);
      setAlerts(a.data.alerts);
      setTrends(t.data.trends);
      setError(null);
    } catch (e) {
      setError('Не удалось загрузить метрики пайплайна');
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [windowHours]);

  const loadRuns = useCallback(async (channelId: string) => {
    try {
      const r = await pipelineMetricsAPI.channel(channelId, 10);
      setRuns(r.data.runs);
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);
  useEffect(() => {
    if (selectedChannel) loadRuns(selectedChannel);
  }, [selectedChannel, loadRuns]);
  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(loadAll, 15000);
    return () => clearInterval(id);
  }, [autoRefresh, loadAll]);

  const totalRuns = health.reduce((s, c) => s + c.runs, 0);
  const totalPublished = health.reduce((s, c) => s + c.topics_published, 0);
  const totalErrors = health.reduce((s, c) => s + c.errors_count, 0);
  const llmCalls = health.reduce((s, c) => s + c.llm.llm_calls, 0);
  const llmLatency = health.reduce((s, c) => s + c.llm.llm_avg_latency_ms * c.llm.llm_calls, 0);
  const tokensOut = health.reduce((s, c) => s + c.llm.tokens_out, 0);
  const avgLlm = llmCalls > 0 ? Math.round(llmLatency / llmCalls) : 0;
  const criticalAlerts = alerts.filter((a) => a.severity === 'critical').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Gauge size={24} className="text-blue-400" /> Pipeline Metrics
          </h1>
          <p className="text-gray-400 text-sm">Observability: тайминги стадий, LLM-метрики, алерты</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={windowHours}
            onChange={(e) => setWindowHours(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2"
          >
            <option value={6}>6 часов</option>
            <option value={24}>24 часа</option>
            <option value={72}>3 дня</option>
            <option value={168}>7 дней</option>
          </select>
          <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
            <input type="checkbox" checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)} />
            Auto-refresh 15s
          </label>
          <button
            onClick={() => loadAll()}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg px-3 py-2"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Обновить
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-300 rounded-lg p-4 text-sm">{error}</div>
      )}

      {/* KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <KpiCard icon={<Activity size={16} />} label="Прогонов" value={String(totalRuns)} sub={`окно ${windowHours}ч`} />
        <KpiCard icon={<Send size={16} />} label="Опубликовано" value={String(totalPublished)} sub="тем за окно" />
        <KpiCard icon={<AlertTriangle size={16} />} label="Ошибок" value={String(totalErrors)} sub={`крит. алертов: ${criticalAlerts}`} />
        <KpiCard icon={<Clock size={16} />} label="Ср. прогон" value={health.length ? sec(Math.round(health.reduce((s, c) => s + c.total_ms.avg, 0) / health.length)) + 's' : '—'} sub="по каналам" />
        <KpiCard icon={<Timer size={16} />} label="LLM латентность" value={avgLlm ? sec(avgLlm) + 's' : '—'} sub={`вызовов: ${llmCalls}`} />
        <KpiCard icon={<Coins size={16} />} label="Tokens out" value={String(tokensOut)} sub="суммарно за окно" />
      </div>

      {/* Trends chart */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
        <h2 className="text-white font-semibold mb-3 flex items-center gap-2">
          <Zap size={16} className="text-yellow-400" /> Тренды по часам
        </h2>
        {trends.length === 0 ? (
          <p className="text-gray-500 text-sm">Нет данных за выбранное окно</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends.map((t) => ({ ...t, hour: t.hour.slice(11, 16) }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="hour" stroke="#9ca3af" fontSize={12} />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
                <Legend />
                <Area type="monotone" dataKey="runs" name="Прогоны" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
                <Area type="monotone" dataKey="published" name="Опубликовано" stroke="#22c55e" fill="#22c55e" fillOpacity={0.2} />
                <Area type="monotone" dataKey="errors" name="Ошибки" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Alerts */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
        <h2 className="text-white font-semibold mb-3 flex items-center gap-2">
          <AlertTriangle size={16} className="text-red-400" /> Алерты ({alerts.length})
        </h2>
        {alerts.length === 0 ? (
          <p className="text-green-400 text-sm flex items-center gap-2">
            <CheckCircle2 size={16} /> Активных алертов нет
          </p>
        ) : (
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {alerts.map((a, i) => (
              <div key={i} className={`border rounded-lg p-3 flex items-start gap-3 ${statusBg(a.severity === 'critical' ? 'critical' : 'warning')}`}>
                {severityIcon(a.severity)}
                <div className="min-w-0">
                  <div className="text-sm text-white">
                    <span className="font-mono text-xs text-gray-400 uppercase mr-2">{a.type}</span>
                    {a.channel_name}
                  </div>
                  <div className="text-xs text-gray-300 mt-1 break-words">{a.message}</div>
                  {a.execution_id && <div className="text-xs text-gray-500 mt-1 font-mono">{a.execution_id}</div>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Channel health table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
        <h2 className="text-white font-semibold mb-3 flex items-center gap-2">
          <Activity size={16} className="text-blue-400" /> Channel Health
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 text-left border-b border-gray-700">
                <th className="py-2 pr-4">Канал</th>
                <th className="py-2 pr-4">Статус</th>
                <th className="py-2 pr-4">Прогоны</th>
                <th className="py-2 pr-4">Success</th>
                <th className="py-2 pr-4">Опубликовано</th>
                <th className="py-2 pr-4">P50</th>
                <th className="py-2 pr-4">P95</th>
                <th className="py-2 pr-4">LLM ср.</th>
                <th className="py-2 pr-4">LLM err</th>
                <th className="py-2 pr-4">Tokens out</th>
                <th className="py-2">Последний прогон</th>
              </tr>
            </thead>
            <tbody>
              {health.map((c) => (
                <tr
                  key={c.channel_id}
                  onClick={() => setSelectedChannel(c.channel_id === selectedChannel ? null : c.channel_id)}
                  className={`border-b border-gray-700/50 cursor-pointer hover:bg-gray-700/30 ${selectedChannel === c.channel_id ? 'bg-gray-700/40' : ''}`}
                >
                  <td className="py-2 pr-4 text-white">{c.channel_name}</td>
                  <td className={`py-2 pr-4 font-semibold ${statusColor(c.status)}`}>{c.status}</td>
                  <td className="py-2 pr-4 text-gray-300">{c.runs}</td>
                  <td className="py-2 pr-4 text-gray-300">{c.success_rate}%</td>
                  <td className="py-2 pr-4 text-gray-300">{c.topics_published}</td>
                  <td className="py-2 pr-4 text-gray-300">{sec(c.total_ms.p50)}s</td>
                  <td className={`py-2 pr-4 ${c.total_ms.p95 > 779600 ? 'text-yellow-400' : 'text-gray-300'}`}>{sec(c.total_ms.p95)}s</td>
                  <td className="py-2 pr-4 text-gray-300">{c.llm.llm_calls > 0 ? sec(c.llm.llm_avg_latency_ms) + 's' : '—'}</td>
                  <td className={`py-2 pr-4 ${c.llm.llm_errors > 0 ? 'text-red-400' : 'text-gray-300'}`}>{c.llm.llm_errors}</td>
                  <td className="py-2 pr-4 text-gray-300">{c.llm.tokens_out}</td>
                  <td className="py-2 text-gray-500 text-xs">{c.last_run_at ? new Date(c.last_run_at).toLocaleString('ru-RU') : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected channel runs */}
      {selectedChannel && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <h2 className="text-white font-semibold mb-3 flex items-center gap-2">
            <Clock size={16} className="text-purple-400" />
            История прогонов: {health.find((c) => c.channel_id === selectedChannel)?.channel_name || selectedChannel}
          </h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {runs.map((r) => (
              <div key={r.id} className="bg-gray-900 rounded-lg p-3 border border-gray-700">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2 text-sm">
                    {r.success
                      ? <CheckCircle2 size={14} className="text-green-400" />
                      : <AlertTriangle size={14} className="text-red-400" />}
                    <span className="font-mono text-gray-300">{r.execution_id || r.id}</span>
                  </div>
                  <span className="text-xs text-gray-500">{r.created_at ? new Date(r.created_at).toLocaleString('ru-RU') : '—'}</span>
                </div>
                <div className="mt-2 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2 text-xs">
                  <div><span className="text-gray-500">Total:</span> <span className="text-white">{sec(r.total_ms)}s</span></div>
                  <div><span className="text-gray-500">Research:</span> <span className="text-gray-300">{sec(r.stage_timings_ms.research)}s</span></div>
                  <div><span className="text-gray-500">Writing:</span> <span className="text-blue-300">{sec(r.stage_timings_ms.writing)}s</span></div>
                  <div><span className="text-gray-500">Media:</span> <span className="text-gray-300">{sec(r.stage_timings_ms.media)}s</span></div>
                  <div><span className="text-gray-500">Publish:</span> <span className="text-gray-300">{sec(r.stage_timings_ms.publishing)}s</span></div>
                  <div><span className="text-gray-500">LLM:</span> <span className="text-gray-300">{r.llm.llm_calls} выз. / {r.llm.llm_errors} err</span></div>
                  <div><span className="text-gray-500">Tokens:</span> <span className="text-gray-300">{r.llm.tokens_in}→{r.llm.tokens_out}</span></div>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  Тем: {r.topics.found} найдено / {r.topics.generated} сгенерировано / <span className="text-green-400">{r.topics.published} опубликовано</span>
                  {r.llm.llm_model && <span className="ml-2">· {r.llm.llm_model}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PipelineDashboard;
