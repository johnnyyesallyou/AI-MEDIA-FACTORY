import pathlib, re
p = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = p.read_text(encoding='utf-8')

# 1. Добавляем иконку Clock в импорт
if 'Clock' not in s.split('\n')[2]:
    s = s.replace(
        "import { Plus, Radio, Globe, Type, Settings, Trash2, Edit2, MessageCircle, CheckCircle, XCircle } from 'lucide-react';",
        "import { Plus, Radio, Globe, Type, Settings, Trash2, Edit2, MessageCircle, CheckCircle, XCircle, Clock } from 'lucide-react';"
    )

# 2. Добавляем состояния для расписания
if 'showScheduleModal' not in s:
    states = '''  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({
    cron_expression: '0 */3 * * *',
    timezone: 'Europe/Moscow',
    max_posts_per_day: 3,
    auto_publish: true,
    is_active: true,
  });
  const [scheduleLoading, setScheduleLoading] = useState(false);
  const [scheduleSaving, setScheduleSaving] = useState(false);
'''
    s = s.replace(
        "  const [connecting, setConnecting] = useState(false);",
        "  const [connecting, setConnecting] = useState(false);\n" + states
    )

# 3. Добавляем функции openScheduleModal и handleSaveSchedule
if 'openScheduleModal' not in s:
    funcs = '''
  const openScheduleModal = async (channelId: string) => {
    setSelectedChannelId(channelId);
    setShowScheduleModal(true);
    setScheduleLoading(true);
    try {
      const r = await channelsAPI.getSchedule(channelId);
      setScheduleForm({
        cron_expression: r.data.cron_expression,
        timezone: r.data.timezone,
        max_posts_per_day: r.data.max_posts_per_day,
        auto_publish: r.data.auto_publish,
        is_active: r.data.is_active,
      });
    } catch (e: any) {
      // 404 — расписания нет, оставляем дефолты
      if (e?.response?.status !== 404) {
        console.error('Error loading schedule:', e);
      }
      setScheduleForm({
        cron_expression: '0 */3 * * *',
        timezone: 'Europe/Moscow',
        max_posts_per_day: 3,
        auto_publish: true,
        is_active: true,
      });
    } finally {
      setScheduleLoading(false);
    }
  };

  const handleSaveSchedule = async () => {
    if (!selectedChannelId) return;
    setScheduleSaving(true);
    try {
      await channelsAPI.updateSchedule(selectedChannelId, scheduleForm);
      alert('Расписание сохранено!');
      setShowScheduleModal(false);
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e.message || 'Unknown error';
      alert('Ошибка сохранения: ' + msg);
    } finally {
      setScheduleSaving(false);
    }
  };

  const cronPresets = [
    { label: 'Каждый час', value: '0 * * * *' },
    { label: 'Каждые 2 часа', value: '0 */2 * * *' },
    { label: 'Каждые 3 часа', value: '0 */3 * * *' },
    { label: 'Каждые 6 часов', value: '0 */6 * * *' },
    { label: 'Дважды в день (9:00, 18:00)', value: '0 9,18 * * *' },
    { label: 'Каждый день в 10:00', value: '0 10 * * *' },
    { label: 'Только будни в 9:00', value: '0 9 * * 1-5' },
  ];
'''
    s = s.replace(
        "  const handleConnectTelegram = async () => {",
        funcs + "\n  const handleConnectTelegram = async () => {"
    )

# 4. Превращаем неактивную кнопку Settings в активную (открывает schedule modal)
s = s.replace(
    '<button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded">\n                    <Settings size={18} />\n                  </button>',
    '<button\n                    onClick={() => openScheduleModal(channel.id)}\n                    className="p-2 text-gray-400 hover:text-purple-400 hover:bg-gray-700 rounded"\n                    title="Расписание публикаций"\n                  >\n                    <Clock size={18} />\n                  </button>'
)

# 5. Добавляем модалку расписания перед закрывающим </div> (после Telegram-модалки)
if 'showScheduleModal && (' not in s:
    modal = '''
      {/* Modal for schedule */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-lg border border-gray-700 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <Clock className="mr-2 text-purple-400" />
              Расписание публикаций
            </h2>

            {scheduleLoading ? (
              <div className="text-center text-gray-400 py-8">Загрузка...</div>
            ) : (
              <div className="space-y-5">
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Cron-выражение</label>
                  <input
                    type="text"
                    value={scheduleForm.cron_expression}
                    onChange={(e) => setScheduleForm({...scheduleForm, cron_expression: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white font-mono focus:outline-none focus:border-purple-500"
                    placeholder="0 */3 * * *"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Формат: минута час день месяц день_недели
                  </p>
                </div>

                <div>
                  <label className="block text-gray-400 text-sm mb-2">Быстрые пресеты</label>
                  <div className="grid grid-cols-2 gap-2">
                    {cronPresets.map((p) => (
                      <button
                        key={p.value}
                        onClick={() => setScheduleForm({...scheduleForm, cron_expression: p.value})}
                        className={`px-3 py-2 text-sm rounded-lg border ${
                          scheduleForm.cron_expression === p.value
                            ? 'bg-purple-600 border-purple-500 text-white'
                            : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-gray-400 text-sm mb-2">Часовой пояс</label>
                  <select
                    value={scheduleForm.timezone}
                    onChange={(e) => setScheduleForm({...scheduleForm, timezone: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  >
                    <option value="Europe/Moscow">Europe/Moscow</option>
                    <option value="Europe/London">Europe/London</option>
                    <option value="Europe/Berlin">Europe/Berlin</option>
                    <option value="America/New_York">America/New_York</option>
                    <option value="America/Los_Angeles">America/Los_Angeles</option>
                    <option value="Asia/Tokyo">Asia/Tokyo</option>
                    <option value="UTC">UTC</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-400 text-sm mb-2">
                    Максимум постов в день: <span className="text-white font-bold">{scheduleForm.max_posts_per_day}</span>
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="20"
                    value={scheduleForm.max_posts_per_day}
                    onChange={(e) => setScheduleForm({...scheduleForm, max_posts_per_day: parseInt(e.target.value)})}
                    className="w-full"
                  />
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div>
                    <div className="text-white text-sm font-medium">Автопубликация</div>
                    <div className="text-xs text-gray-400">Автоматически публиковать одобренные посты</div>
                  </div>
                  <button
                    onClick={() => setScheduleForm({...scheduleForm, auto_publish: !scheduleForm.auto_publish})}
                    className={`relative w-12 h-6 rounded-full transition-colors ${
                      scheduleForm.auto_publish ? 'bg-purple-600' : 'bg-gray-600'
                    }`}
                  >
                    <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                      scheduleForm.auto_publish ? 'translate-x-6' : ''
                    }`} />
                  </button>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div>
                    <div className="text-white text-sm font-medium">Расписание активно</div>
                    <div className="text-xs text-gray-400">Включить автоматический запуск</div>
                  </div>
                  <button
                    onClick={() => setScheduleForm({...scheduleForm, is_active: !scheduleForm.is_active})}
                    className={`relative w-12 h-6 rounded-full transition-colors ${
                      scheduleForm.is_active ? 'bg-green-600' : 'bg-gray-600'
                    }`}
                  >
                    <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                      scheduleForm.is_active ? 'translate-x-6' : ''
                    }`} />
                  </button>
                </div>
              </div>
            )}

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleSaveSchedule}
                disabled={scheduleLoading || scheduleSaving}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              >
                {scheduleSaving ? 'Сохранение...' : 'Сохранить'}
              </button>
              <button
                onClick={() => setShowScheduleModal(false)}
                disabled={scheduleSaving}
                className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
'''
    # Вставляем перед последним </div>
    s = s.rstrip()
    if s.endswith('</div>'):
        s = s[:-6] + modal + '    </div>\n  );\n};\n\nexport default Channels;\n'
        p.write_text(s, encoding='utf-8')
        print('OK Channels.tsx: schedule modal added')
    else:
        print('ERROR: unexpected end of file')