import pathlib

p = pathlib.Path('./frontend/src/pages/Logs.tsx')
s = p.read_text(encoding='utf-8').replace('\r\n', '\n')
changed = []

# 1. Импорт automationAPI + RefreshCw
if 'automationAPI' not in s:
    s = s.replace(
        "import { logsAPI } from '../api/client';",
        "import { logsAPI, automationAPI } from '../api/client';"
    )
    changed.append('import_api')

if 'RefreshCw' not in s:
    s = s.replace(
        "import { ScrollText, Clock, CheckCircle, XCircle, AlertCircle, Eye, ChevronRight } from 'lucide-react';",
        "import { ScrollText, Clock, CheckCircle, XCircle, AlertCircle, Eye, ChevronRight, RefreshCw } from 'lucide-react';"
    )
    changed.append('import_icon')

# 2. Состояние retryingStage (после selectedLog)
if 'retryingStage' not in s:
    s = s.replace(
        'const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);',
        'const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);\n  const [retryingStage, setRetryingStage] = useState<string | null>(null);'
    )
    changed.append('state')

# 3. Функция handleRetry (после loadLogs)
if 'handleRetry' not in s:
    handler = '''
  const handleRetry = async (executionId: string, stageName: string) => {
    setRetryingStage(stageName);
    try {
      const r = await automationAPI.retry(executionId, stageName);
      const newId = r.data.new_execution_id || 'retry started';
      alert(`Этап "${stageName}" перезапущен! ID: ${newId}\\nПроверьте результат через 30-60 секунд.`);
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

'''
    s = s.replace(
        '  const getStepIcon = (status: string) => {',
        handler + '  const getStepIcon = (status: string) => {'
    )
    changed.append('handler')

# 4. Кнопка Retry после бейджа (только для failed)
old_badge_line = '''                        {getStepBadge(step.status)}
                      </div>'''

new_badge_line = '''                        {getStepBadge(step.status)}
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
                      </div>'''

if old_badge_line in s:
    s = s.replace(old_badge_line, new_badge_line)
    changed.append('button')
else:
    print('WARN: badge anchor not found, checking exact format...')
    # Альтернатива: ищем по бейджу
    import re
    pattern = re.compile(r'(\s+)\{getStepBadge\(step\.status\)\}\n(\s+)</div>')
    m = pattern.search(s)
    if m:
        indent1, indent2 = m.group(1), m.group(2)
        replacement = f'''{indent1}{{getStepBadge(step.status)}}
{indent1}{{step.status === 'failed' && selectedLog && (
{indent1}  <button
{indent1}    onClick={{() => handleRetry(selectedLog.execution_id || selectedLog.id, step.step_name)}}
{indent1}    disabled={{retryingStage === step.step_name}}
{indent1}    className="ml-2 flex items-center gap-1 px-2 py-1 bg-orange-600/30 hover:bg-orange-600/50 text-orange-300 rounded text-xs font-medium disabled:opacity-50 transition"
{indent1}    title="Повторить этот этап"
{indent1}  >
{indent1}    <RefreshCw size={{12}} className={{retryingStage === step.step_name ? 'animate-spin' : ''}} />
{indent1}    {{retryingStage === step.step_name ? 'Запуск...' : 'Повторить'}}
{indent1}  </button>
{indent1})}}
{indent2}</div>'''
        s = s[:m.start()] + replacement + s[m.end():]
        changed.append('button_regex')

# 5. Добавляем execution_id в интерфейс LogEntry (если нет)
if 'execution_id' not in s:
    s = s.replace(
        'interface LogEntry {\n  id: string;',
        'interface LogEntry {\n  id: string;\n  execution_id?: string;'
    )
    changed.append('interface')

p.write_text(s, encoding='utf-8')
print(f'OK: Logs.tsx patched: {", ".join(changed)}')