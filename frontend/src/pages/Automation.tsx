import React, { useEffect, useState } from 'react';
import { automationAPI, channelsAPI, logsAPI } from '../api/client';
import { Play, RefreshCw, Clock, Calendar, CheckCircle, XCircle, Radio } from 'lucide-react';

interface ScheduleInfo {
  channel_id: string;
  channel_name: string;
  cron_expression?: string;
  timezone?: string;
  is_active?: boolean;
  last_run?: string | null;
  next_run?: string | null;
}

const Automation: React.FC = () => {
  const [status, setStatus] = useState<any>(null);
  const [schedules, setSchedules] = useState<ScheduleInfo[]>([]);
  const [runs, setRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [st, ch, lg] = await Promise.all([
        automationAPI.getSchedulerStatus(),
        channelsAPI.list(),
        logsAPI.list(8),
      ]);
      setStatus(st.data);
      setRuns(lg.data.items || []);

      const chans = ch.data.channels || [];
      const merged: ScheduleInfo[] = [];
      for (const c of chans) {
        try {
          const sr = await channelsAPI.getSchedule(c.id);
          merged.push({ ...sr.data, channel_name: c.name });
        } catch (e) {
          merged.push({ channel_id: c.id, channel_name: c.name });
        }
      }
      setSchedules(merged);
    } catch (e) {
      console.error('Error loading scheduler dashboard:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleRunNow = async () => {
    setRunning(true);
    try {
      await automationAPI.runNow();
      alert('Пайплайн запущен для всех активных каналов! Результаты — во вкладке Logs.');
      setTimeout(loadData, 5000);
    } catch (e) {
      console.error(e);
      alert('Ошибка запуска пайплайна');
    } finally {
      setRunning(false);
    }
  };

  const fmt = (d?: string | null) => (d ? new Date(d).toLocaleString('ru-RU') : '—');

  const nextRuns = schedules
    .filter(s => s.next_run)
    .sort((a, b) => (a.next_run! < b.next_run! ? -1 : 1));

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Scheduler Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Персональные расписания каналов и история запусков</p>
        </div>
        <div className="flex gap-2">
          <button onClick={loadData} className="p-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600" title="Обновить">
            <RefreshCw size={18} />
          </button>
          <button
            onClick={handleRunNow}
            disabled={running}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            <Play size={18} className="mr-2" />
            {running ? 'Запуск...' : 'Запустить сейчас'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Загрузка...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-800 rounded-lg p-5 border border-gray-700">
              <div className="flex items-center text-gray-400 text-sm mb-2"><Radio size={16} className="mr-2" />Планировщик</div>
              <div className={'text-xl font-bold ' + (status && status.running ? 'text-green-400' : 'text-red-400')}>
                {status && status.running ? '● Активен' : '○ Остановлен'}
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg p-5 border border-gray-700">
              <div className="flex items-center text-gray-400 text-sm mb-2"><Calendar size={16} className="mr-2" />Активных расписаний</div>
              <div className="text-xl font-bold text-white">{schedules.filter(s => s.is_active).length} из {schedules.length}</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-5 border border-gray-700">
              <div className="flex items-center text-gray-400 text-sm mb-2"><Clock size={16} className="mr-2" />Ближайший запуск</div>
              <div className="text-xl font-bold text-purple-400">{nextRuns.length ? fmt(nextRuns[0].next_run) : '—'}</div>
              {nextRuns.length > 0 && <div className="text-xs text-gray-500 mt-1">{nextRuns[0].channel_name}</div>}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 mb-6">
            <h2 className="text-lg font-semibold text-white mb-4">Расписания каналов</h2>
            <div className="space-y-3">
              {schedules.map(s => (
                <div key={s.channel_id} className="flex flex-wrap items-center justify-between gap-3 bg-gray-700/50 rounded-lg p-4">
                  <div>
                    <div className="text-white font-medium">{s.channel_name}</div>
                    <div className="text-xs text-gray-500 mt-1">Последний запуск: {fmt(s.last_run)}</div>
                  </div>
                  <div className="text-right">
                    {s.cron_expression ? (
                      <>
                        <div className="font-mono text-purple-300">{s.cron_expression} <span className="text-gray-500">({s.timezone})</span></div>
                        <div className="text-xs text-purple-400 mt-1">Следующий: {fmt(s.next_run)}</div>
                      </>
                    ) : (
                      <div className="text-xs text-gray-500">Расписание не настроено (задайте в Channels)</div>
                    )}
                  </div>
                  <span className={'px-3 py-1 rounded text-xs ' + (s.is_active ? 'bg-green-500/20 text-green-400' : 'bg-gray-600/40 text-gray-400')}>
                    {s.is_active ? 'Активно' : 'Пауза'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Последние запуски пайплайна</h2>
            <div className="space-y-3">
              {runs.map(r => (
                <div key={r.id} className="bg-gray-700/50 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <div className="text-white text-sm font-medium">{r.headline || 'Без заголовка'}</div>
                    <div className="text-xs text-gray-500">{fmt(r.timestamp || r.created_at)} · {(r.total_duration_ms / 1000).toFixed(1)}s</div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(r.pipeline_steps || []).map((st: any) => (
                      <span key={st.step_name} className={'flex items-center text-xs px-2 py-1 rounded ' + (st.status === 'success' ? 'bg-green-500/10 text-green-400' : st.status === 'failed' ? 'bg-red-500/10 text-red-400' : 'bg-gray-600/30 text-gray-400')}>
                        {st.status === 'success' ? <CheckCircle size={12} className="mr-1" /> : <XCircle size={12} className="mr-1" />}
                        {st.step_name}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Automation;
