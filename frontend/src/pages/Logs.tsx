import React, { useEffect, useState } from 'react';
import { logsAPI, automationAPI } from '../api/client';
import { ScrollText, Clock, CheckCircle, XCircle, AlertCircle, Eye, ChevronRight, RefreshCw } from 'lucide-react';

interface PipelineStep {
  step_name: string;
  status: string;
  duration_ms: number;
  details: string;
}

interface LogEntry {
  id: string;
  execution_id?: string;
  timestamp: string;
  content_id: string;
  headline: string;
  pipeline_steps: PipelineStep[];
  total_duration_ms: number;
}

const Logs: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);
  const [retryingStage, setRetryingStage] = useState<string | null>(null);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const response = await logsAPI.list(50);
      setLogs((response.data.items || []).map((l: any) => ({ ...l, timestamp: l.created_at || l.timestamp })));
    } catch (error) {
      console.error('Error loading logs:', error);
    } finally {
      setLoading(false);
    }
  };


  const handleRetry = async (executionId: string, stageName: string) => {
    setRetryingStage(stageName);
    try {
      const r = await automationAPI.retry(executionId, stageName);
      const newId = r.data.new_execution_id || 'retry started';
      alert(`Этап "${stageName}" перезапущен! ID: ${newId}\nПроверьте результат через 30-60 секунд.`);
      // Автообновление через 5 сек
      setTimeout(() => {
        loadLogs();
        setSelectedLog(null);
      }, 5000);
    } catch (e: any) {
      console.error('Retry failed:', e);
      alert(`Ошибка retry: ${e?.response?.data?.detail || e.message}`);
    } finally {
      setRetryingStage(null);
    }
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle size={16} className="text-green-400" />;
      case 'failed': return <XCircle size={16} className="text-red-400" />;
      case 'skipped': return <AlertCircle size={16} className="text-gray-400" />;
      default: return <Clock size={16} className="text-yellow-400" />;
    }
  };

  const getStepBadge = (status: string) => {
    const styles: Record<string, string> = {
      success: 'bg-green-500/20 text-green-400',
      failed: 'bg-red-500/20 text-red-400',
      skipped: 'bg-gray-500/20 text-gray-400',
      running: 'bg-yellow-500/20 text-yellow-400',
    };
    const labels: Record<string, string> = {
      success: 'Успех',
      failed: 'Ошибка',
      skipped: 'Пропущено',
      running: 'Выполняется',
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[status] || styles.running}`}>
        {labels[status] || status}
      </span>
    );
  };

  const formatDuration = (ms: number) => {
    if (ms >= 1000) {
      return `${(ms / 1000).toFixed(1)}s`;
    }
    return `${ms}ms`;
  };

  const getStepLabel = (stepName: string) => {
    const labels: Record<string, string> = {
      research: 'Research',
      writing: 'Writing',
      fact_check: 'Fact Check',
      publishing: 'Publishing',
      decision: 'Decision',
      brief: 'Brief',
      image: 'Image',
      evaluator: 'Evaluator',
    };
    return labels[stepName] || stepName;
  };

  if (loading) {
    return <div className="text-center text-gray-400 py-12">Загрузка логов...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <ScrollText size={32} className="mr-3 text-orange-400" />
            Logs
          </h1>
          <p className="text-gray-400 mt-1">Журнал операций и трассировка пайплайна</p>
        </div>
        <button
          onClick={loadLogs}
          className="flex items-center px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
        >
          <Clock size={18} className="mr-2" />
          Обновить
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Всего операций</div>
          <div className="text-2xl font-bold text-white">{logs.length}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Успешных</div>
          <div className="text-2xl font-bold text-green-400">
            {logs.filter(log => log.pipeline_steps.every(s => s.status === 'success')).length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">С ошибками</div>
          <div className="text-2xl font-bold text-red-400">
            {logs.filter(log => log.pipeline_steps.some(s => s.status === 'failed')).length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Среднее время</div>
          <div className="text-2xl font-bold text-blue-400">
            {logs.length > 0 ? formatDuration(logs.reduce((acc, log) => acc + log.total_duration_ms, 0) / logs.length) : '0ms'}
          </div>
        </div>
      </div>

      {/* Logs List */}
      {logs.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
          <ScrollText size={48} className="mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold text-white mb-2">Логов пока нет</h3>
          <p className="text-gray-400">Операции будут отображаться здесь</p>
        </div>
      ) : (
        <div className="space-y-4">
          {logs.map((log) => (
            <div key={log.id} className="bg-gray-800 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors">
              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-1">{log.headline}</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span className="flex items-center">
                        <Clock size={14} className="mr-1" />
                        {new Date(log.timestamp).toLocaleString('ru-RU')}
                      </span>
                      <span>ID: {(log.content_id || "").substring(0, 8)}...</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500 mb-1">Общее время</div>
                    <div className="text-xl font-bold text-blue-400">
                      {formatDuration(log.total_duration_ms)}
                    </div>
                  </div>
                </div>

                {/* Pipeline Steps Preview */}
                <div className="flex items-center gap-2 mb-3 overflow-x-auto pb-2">
                  {log.pipeline_steps.map((step, idx) => (
                    <React.Fragment key={idx}>
                      <div className="flex items-center gap-2 bg-gray-900/50 px-3 py-2 rounded border border-gray-700/50">
                        {getStepIcon(step.status)}
                        <span className="text-sm text-gray-300 whitespace-nowrap">{getStepLabel(step.step_name)}</span>
                        <span className="text-xs text-gray-500">{formatDuration(step.duration_ms)}</span>
                      </div>
                      {idx < log.pipeline_steps.length - 1 && (
                        <ChevronRight size={16} className="text-gray-600" />
                      )}
                    </React.Fragment>
                  ))}
                </div>

                <button
                  onClick={() => setSelectedLog(log)}
                  className="flex items-center text-sm text-blue-400 hover:text-blue-300 transition-colors"
                >
                  <Eye size={14} className="mr-1" />
                  Подробнее
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto border border-gray-700">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">{selectedLog.headline}</h2>
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span className="flex items-center">
                      <Clock size={14} className="mr-1" />
                      {new Date(selectedLog.timestamp).toLocaleString('ru-RU')}
                    </span>
                    <span>Общее время: <span className="text-blue-400 font-semibold">{formatDuration(selectedLog.total_duration_ms)}</span></span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedLog(null)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>

              <h3 className="text-lg font-semibold text-white mb-4">Трассировка пайплайна</h3>
              
              <div className="space-y-3">
                {selectedLog.pipeline_steps.map((step, idx) => (
                  <div key={idx} className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        {getStepIcon(step.status)}
                        <span className="font-semibold text-white">{getStepLabel(step.step_name)}</span>
                        {getStepBadge(step.status)}
                        {step.status === 'failed' && selectedLog && (
                          <button
                            onClick={() => handleRetry(selectedLog.execution_id || selectedLog.id, step.step_name)}
                            disabled={retryingStage === step.step_name}
                            className="ml-2 flex items-center gap-1 px-2 py-1 bg-orange-600/30 hover:bg-orange-600/50 text-orange-300 rounded text-xs font-medium disabled:opacity-50 transition"
                            title="Повторить этот этап"
                          >
                            <RefreshCw size={12} className={retryingStage === step.step_name ? 'animate-spin' : ''} />
                            {retryingStage === step.step_name ? 'Запуск...' : 'Повторить'}
                          </button>
                        )}
                      </div>
                      <span className="text-sm text-gray-400">{formatDuration(step.duration_ms)}</span>
                    </div>
                    {step.details && (
                      <p className="text-sm text-gray-400 mt-2 pl-7">{step.details}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Logs;
