import pathlib
p = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = p.read_text(encoding='utf-8').replace('\r\n', '\n')

# 1. Добавляем импорт automationAPI
if 'automationAPI' not in s:
    s = s.replace(
        "import { channelsAPI } from '../api/client';",
        "import { channelsAPI, automationAPI } from '../api/client';"
    )

# 2. Добавляем состояния для расписаний
if 'channelSchedules' not in s:
    s = s.replace(
        '  const [scheduleSaving, setScheduleSaving] = useState(false);',
        '  const [scheduleSaving, setScheduleSaving] = useState(false);\n  const [channelSchedules, setChannelSchedules] = useState<{[key: string]: any}>({});'
    )

# 3. Добавляем функцию загрузки расписаний
if 'loadAllSchedules' not in s:
    func = '''
  const loadAllSchedules = async () => {
    try {
      const status = await automationAPI.getSchedulerStatus();
      const schedules: {[key: string]: any} = {};
      
      // Для каждого канала загружаем его расписание
      for (const channel of channels) {
        try {
          const r = await channelsAPI.getSchedule(channel.id);
          schedules[channel.id] = r.data;
        } catch (e: any) {
          if (e?.response?.status !== 404) {
            console.error('Error loading schedule for', channel.id, e);
          }
        }
      }
      setChannelSchedules(schedules);
    } catch (e) {
      console.error('Error loading scheduler status:', e);
    }
  };

'''
    s = s.replace('  useEffect(() => {\n    loadChannels();', func + '  useEffect(() => {\n    loadChannels();')

# 4. Вызываем loadAllSchedules после loadChannels
if 'loadAllSchedules()' not in s:
    s = s.replace(
      '  const loadChannels = async () => {\n    try {\n      const response = await channelsAPI.list();\n      setChannels(response.data.channels || []);\n    } catch (error) {\n      console.error(\'Error loading channels:\', error);\n    } finally {\n      setLoading(false);\n    }\n  };',
      '  const loadChannels = async () => {\n    try {\n      const response = await channelsAPI.list();\n      setChannels(response.data.channels || []);\n      // Загружаем расписания после загрузки каналов\n      setTimeout(() => loadAllSchedules(), 500);\n    } catch (error) {\n      console.error(\'Error loading channels:\', error);\n    } finally {\n      setLoading(false);\n    }\n  };'
    )

# 5. Добавляем отображение next_run на карточке (после description)
if 'channelSchedules[channel.id]' not in s:
    schedule_block = '''                  {channel.description && (
                    <p className="text-gray-400 mt-3 text-sm">{channel.description}</p>
                  )}

                  {channelSchedules[channel.id] && (
                    <div className="mt-3 pt-3 border-t border-gray-700">
                      <div className="flex items-center text-sm">
                        <Clock size={16} className="mr-2 text-purple-400" />
                        <span className="text-gray-400">Расписание:</span>
                        <span className="ml-2 text-white font-mono">{channelSchedules[channel.id].cron_expression}</span>
                      </div>
                      {channelSchedules[channel.id].last_run && (
                        <div className="flex items-center text-xs text-gray-500 mt-1">
                          <span className="ml-6">Последний запуск: {new Date(channelSchedules[channel.id].last_run).toLocaleString('ru-RU')}</span>
                        </div>
                      )}
                      {channelSchedules[channel.id].next_run && (
                        <div className="flex items-center text-xs text-purple-400 mt-1">
                          <span className="ml-6">Следующий запуск: {new Date(channelSchedules[channel.id].next_run).toLocaleString('ru-RU')}</span>
                        </div>
                      )}
                    </div>
                  )}
'''
    s = s.replace(
        '                  {channel.description && (\n                    <p className="text-gray-400 mt-3 text-sm">{channel.description}</p>\n                  )}\n',
        schedule_block
    )

p.write_text(s, encoding='utf-8')
print('✅ Channels.tsx: добавлено отображение next_run/last_run')