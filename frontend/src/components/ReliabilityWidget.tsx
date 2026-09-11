import React, { useEffect, useState, useCallback } from 'react';
import apiClient from '../api/client';

interface DLQStats {
  total: number;
  unresolved: number;
  by_type: Record<string, number>;
  by_channel: Record<string, number>;
}

interface BreakerSnapshot {
  name: string;
  state: string;
  failure_count: number;
  total_opens: number;
  last_error: string | null;
}

interface HealthStatus {
  status: 'ok' | 'error' | 'unknown';
  latency_ms?: number;
  detail?: string;
}

interface ReliabilityData {
  breakers: Record<string, BreakerSnapshot>;
  channel_pauses: Record<string, number>;
  dead_letters: DLQStats | null;
  self_healing: { running: boolean; last_run: any } | null;
}

const ReliabilityWidget: React.FC = () => {
  const [data, setData] = useState<ReliabilityData | null>(null);
  const [busy, setBusy] = useState(false);
  const [health, setHealth] = useState<Record<string, HealthStatus> | null>(null);
  const [healthBusy, setHealthBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [cb, dlq, sh] = await Promise.all([
        apiClient.get('/reliability/circuit-breakers'),
        apiClient.get('/reliability/dead-letters/stats'),
        apiClient.get('/reliability/self-healing/status'),
      ]);
      setData({
        breakers: cb.data.breakers || {},
        channel_pauses: cb.data.channel_pauses || {},
        dead_letters: dlq.data,
        self_healing: sh.data,
      });
    } catch (e) {
      console.error('Reliability widget load error:', e);
    }
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 60000);
    return () => clearInterval(t);
  }, [load]);

  const runHealthCheck = async () => {
    setHealthBusy(true);
    try {
      const res = await apiClient.get('/reliability/health');
      setHealth(res.data.platforms || { overall: { status: res.data.status, detail: res.data.detail } });
    } catch (e: any) {
      setHealth({ error: { status: 'error', detail: e?.message || 'Health check failed' } });
    } finally {
      setHealthBusy(false);
    }
  };

  const runSelfHealing = async () => {
    setBusy(true);
    try {
      await apiClient.post('/reliability/self-healing/run?limit=20');
      await load();
    } catch (e) {
      console.error('Self-healing trigger error:', e);
    } finally {
      setBusy(false);
    }
  };

  const breakerColor = (state: string) =>
    state === 'closed' ? 'bg-green-500' : state === 'half_open' ? 'bg-yellow-500' : 'bg-red-500';

  const dlq = data?.dead_letters;
  const pauses = data?.channel_pauses || {};
  const pauseCount = Object.keys(pauses).length;

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-white">Reliability — DLQ & Circuit Breakers</h2>
        <div className="flex gap-2">
          <button
            onClick={runHealthCheck}
            disabled={healthBusy}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 text-sm"
          >
            {healthBusy ? 'Проверка...' : 'Health Check'}
          </button>
          <button
            onClick={runSelfHealing}
            disabled={busy}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
          >
            {busy ? 'Запуск...' : 'Запустить Self-Healing'}
          </button>
        </div>
      </div>

      {health && (
        <div className="mb-4 bg-gray-700 rounded-lg p-3">
          <div className="text-gray-400 text-xs mb-2">API Health</div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(health).map(([platform, status]) => (
              <span
                key={platform}
                className={`px-2 py-1 rounded text-xs text-white ${
                  status.status === 'ok' ? 'bg-green-500' : status.status === 'unknown' ? 'bg-gray-500' : 'bg-red-500'
                }`}
              >
                {platform}: {status.status}
                {status.latency_ms != null && ` (${status.latency_ms}ms)`}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-gray-400 text-sm">DLQ unresolved</div>
          <div className={`text-3xl font-bold ${dlq && dlq.unresolved > 0 ? 'text-red-400' : 'text-green-400'}`}>
            {dlq ? dlq.unresolved : '—'}
          </div>
          <div className="text-gray-400 text-xs">всего записей: {dlq?.total ?? '—'}</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Circuit Breakers</div>
          <div className="flex flex-wrap gap-2 mt-2">
            {Object.values(data?.breakers || {}).length === 0 && (
              <span className="text-gray-400 text-xs">нет данных</span>
            )}
            {Object.values(data?.breakers || {}).map((b) => (
              <span key={b.name} className={`px-2 py-1 rounded text-xs text-white ${breakerColor(b.state)}`}>
                {b.name}: {b.state}
              </span>
            ))}
          </div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Каналы на паузе (429)</div>
          <div className={`text-3xl font-bold ${pauseCount > 0 ? 'text-yellow-400' : 'text-green-400'}`}>
            {pauseCount}
          </div>
          <div className="text-gray-400 text-xs">
            Self-healing: {data?.self_healing?.running ? 'активен' : 'ручной режим'}
          </div>
        </div>
      </div>

      {pauseCount > 0 && (
        <div className="mb-3 bg-gray-700 rounded-lg p-3">
          <div className="text-gray-400 text-xs mb-2">Каналы на паузе:</div>
          <div className="space-y-1">
            {Object.entries(pauses)
              .filter(([, remaining]) => remaining > 0)
              .sort(([, a], [, b]) => b - a)
              .map(([channelId, remaining]) => (
                <div key={channelId} className="flex justify-between text-xs">
                  <span className="text-gray-300 font-mono">{channelId}</span>
                  <span className="text-yellow-400">{Math.round(remaining)}s remaining</span>
                </div>
              ))}
          </div>
        </div>
      )}

      {dlq && Object.keys(dlq.by_channel || {}).length > 0 && (
        <div className="mb-3 bg-gray-700 rounded-lg p-3">
          <div className="text-gray-400 text-xs mb-2">DLQ by channel:</div>
          <div className="space-y-1">
            {Object.entries(dlq.by_channel).map(([ch, n]) => (
              <div key={ch} className="flex justify-between text-xs">
                <span className="text-gray-300 font-mono">{ch}</span>
                <span className="text-red-400">{n} unresolved</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {dlq && dlq.unresolved > 0 && Object.keys(dlq.by_type).length > 0 && (
        <div className="text-gray-400 text-xs">
          По типам: {Object.entries(dlq.by_type).map(([t, n]) => `${t}: ${n}`).join(' • ')}
        </div>
      )}
    </div>
  );
};

export default ReliabilityWidget;
