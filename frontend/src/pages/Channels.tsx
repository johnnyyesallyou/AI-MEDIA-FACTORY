import React, { useEffect, useState } from 'react';
import { channelsAPI, automationAPI } from '../api/client, getTemplates, createFromTemplate';
import { Plus, Radio, Globe, Type, Settings, Trash2, Edit2, MessageCircle, CheckCircle, XCircle, Clock } from 'lucide-react';
import ChannelManager from '../components/ChannelManager';

interface Channel {
  id: string;
  name: string;
  platform: string;
  vk_group_id?: string;
  vk_access_token?: string;
  youtube_channel_id?: string;
  youtube_api_key?: string;
  dzen_channel_id?: string;
  dzen_api_key?: string;
  language_search: string;
  language_publish: string;
  style_profile: string;
  timezone: string;
  description?: string;
  is_connected: boolean;
  telegram_bot_token?: string;
  telegram_chat_id?: string;
  sources: any[];
}

const Channels: React.FC = () => {
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [templates, setTemplates] = useState<any[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTelegramModal, setShowTelegramModal] = useState(false);
  const [selectedChannelId, setSelectedChannelId] = useState<string | null>(null);
  const [telegramForm, setTelegramForm] = useState({
    bot_token: '',
    chat_id: ''
  });
  // Sprint 11: Universal platform connection modal (VK/YouTube/Dzen)
  const [showPlatformModal, setShowPlatformModal] = useState(false);
  const [platformType, setPlatformType] = useState<string>('vk');
  const [platformForm, setPlatformForm] = useState<Record<string, string>>({});

  const [connecting, setConnecting] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({
    cron_expression: '0 */3 * * *',
    timezone: 'Europe/Moscow',
    max_posts_per_day: 3,
    auto_publish: true,
    is_active: true,
  });
  const [scheduleLoading, setScheduleLoading] = useState(false);
  const [scheduleSaving, setScheduleSaving] = useState(false);
  const [showManagerModal, setShowManagerModal] = useState(false);
  const [managerChannel, setManagerChannel] = useState<{id: string, name: string} | null>(null);
  const [channelSchedules, setChannelSchedules] = useState<{[key: string]: any}>({});
  const [newChannel, setNewChannel] = useState({
    name: '',
    platform: 'telegram',
    language_search: 'en',
    language_publish: 'ru',
    style_profile: 'minimal',
    timezone: 'UTC',
    description: ''
  });


  const loadAllSchedules = async (chs: any[]) => {
    try {
      const status = await automationAPI.getSchedulerStatus();
      const schedules: {[key: string]: any} = {};
      
      // Для каждого канала загружаем его расписание
      for (const channel of chs) {
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

  useEffect(() => {
    loadChannels();
  }, []);

  
  const loadTemplates = async () => {
    try {
      const response = await channelsAPI.getTemplates();
      setTemplates(response.data);
      setShowTemplateModal(true);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const createChannelFromTemplate = async (templateId: string) => {
    try {
      await channelsAPI.createFromTemplate(templateId);
      setShowTemplateModal(false);
      loadChannels(); // Refresh list
    } catch (error) {
      console.error('Failed to create channel:', error);
    }
  };

  const loadChannels = async () => {
    try {
      const response = await channelsAPI.list();
      setChannels(response.data.channels || []);
      // Загружаем расписания после загрузки каналов
      setTimeout(() => loadAllSchedules(response.data.channels || []), 500);
    } catch (error) {
      console.error('Error loading channels:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateChannel = async () => {
    try {
      await channelsAPI.create(newChannel);
      setShowCreateModal(false);
      setNewChannel({
        name: '',
        platform: 'telegram',
        language_search: 'en',
        language_publish: 'ru',
        style_profile: 'minimal',
        timezone: 'UTC',
        description: ''
      });
      loadChannels();
    } catch (error) {
      console.error('Error creating channel:', error);
      alert('Ошибка создания канала');
    }
  };

  const handleDeleteChannel = async (id: string) => {
    if (confirm('Удалить канал?')) {
      try {
        await channelsAPI.delete(id);
        loadChannels();
      } catch (error) {
        console.error('Error deleting channel:', error);
      }
    }
  };

  const openTelegramModal = (channelId: string) => {
    setSelectedChannelId(channelId);
    const channel = channels.find(c => c.id === channelId);
    setTelegramForm({
      bot_token: channel?.telegram_bot_token || '',
      chat_id: channel?.telegram_chat_id || ''
    });
    setShowTelegramModal(true);
  };
  const openVkModal = (channelId: string) => {
    setSelectedChannelId(channelId);
    const channel = channels.find(c => c.id === channelId);
    setPlatformType('vk');
    setPlatformForm({
      group_id: channel?.vk_group_id || '',
      access_token: channel?.vk_access_token || ''
    });
    setShowPlatformModal(true);
  };

  const openYoutubeModal = (channelId: string) => {
    setSelectedChannelId(channelId);
    const channel = channels.find(c => c.id === channelId);
    setPlatformType('youtube');
    setPlatformForm({
      channel_id: channel?.youtube_channel_id || '',
      api_key: channel?.youtube_api_key || ''
    });
    setShowPlatformModal(true);
  };

  const openDzenModal = (channelId: string) => {
    setSelectedChannelId(channelId);
    const channel = channels.find(c => c.id === channelId);
    setPlatformType('dzen');
    setPlatformForm({
      channel_id: channel?.dzen_channel_id || '',
      api_key: channel?.dzen_api_key || ''
    });
    setShowPlatformModal(true);
  };

  const handleConnectPlatform = async () => {
    if (!selectedChannelId) return;
    setConnecting(true);
    try {
      if (platformType === 'vk') {
        await channelsAPI.connectVk(selectedChannelId, platformForm);
        alert('✅ VK группа успешно подключена!');
      } else if (platformType === 'youtube') {
        await channelsAPI.connectYoutube(selectedChannelId, platformForm);
        alert('✅ YouTube канал успешно подключен!');
      } else if (platformType === 'dzen') {
        await channelsAPI.connectDzen(selectedChannelId, platformForm);
        alert('✅ Дзен канал успешно подключен!');
      }
      setShowPlatformModal(false);
      loadChannels();
    } catch (error) {
      console.error(`Error connecting ${platformType}:`, error);
      alert(`❌ Ошибка подключения: ${(error as Error).message}`);
    } finally {
      setConnecting(false);
    }
  };


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
      if (e?.response?.status !== 404) console.error('Error loading schedule:', e);
      setScheduleForm({ cron_expression: '0 */3 * * *', timezone: 'Europe/Moscow', max_posts_per_day: 3, auto_publish: true, is_active: true });
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
    { label: 'Будни в 9:00', value: '0 9 * * 1-5' },
  ];

  const handleConnectTelegram = async () => {
    if (!selectedChannelId) return;
    setConnecting(true);
    try {
      await channelsAPI.connectTelegram(selectedChannelId, telegramForm);
      alert('Telegram бот успешно подключен!');
      setShowTelegramModal(false);
      loadChannels();
    } catch (error) {
      console.error('Error connecting Telegram:', error);
      alert('Ошибка подключения Telegram бота');
    } finally {
      setConnecting(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-white">Channels</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus size={20} className="mr-2" />
          Новый канал
        </button>
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Загрузка...</div>
      ) : channels.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
          <Radio size={48} className="mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold text-white mb-2">Каналов пока нет</h3>
          <p className="text-gray-400 mb-4">Создайте первый канал для начала работы</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Создать канал
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {channels.map((channel) => (
            <div key={channel.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center mb-3">
                    <h3 className="text-xl font-bold text-white mr-3">{channel.name}</h3>
                    <span className={`px-3 py-1 rounded text-xs ${
                      channel.is_connected ? 'bg-green-500' : 'bg-red-500'
                    }`}>
                      {channel.is_connected ? '✓ Connected' : '○ Disconnected'}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                    <div className="flex items-center text-gray-400">
                      <Globe size={16} className="mr-2" />
                      {channel.platform}
                    </div>
                    <div className="flex items-center text-gray-400">
                      <Type size={16} className="mr-2" />
                      {channel.language_search} → {channel.language_publish}
                    </div>
                    <div className="text-gray-400">
                      Стиль: {channel.style_profile}
                    </div>
                  </div>

                  {channel.description && (
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

                  {channel.platform === 'telegram' && (
                    <div className="mt-4 pt-4 border-t border-gray-700">
                      {channel.is_connected ? (
                        <div className="flex items-center text-green-400 text-sm">
                          <CheckCircle size={16} className="mr-2" />
                          Telegram бот подключен
                          {channel.telegram_chat_id && (
                            <span className="ml-2 text-gray-500">({channel.telegram_chat_id})</span>
                          )}
                        </div>
                      ) : (
                        <div className="flex items-center text-gray-500 text-sm">
                          <XCircle size={16} className="mr-2" />
                          Telegram бот не подключен
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  {channel.platform === 'telegram' && (
                    <button
                      onClick={() => openTelegramModal(channel.id)}
                      className="p-2 text-blue-400 hover:text-blue-300 hover:bg-gray-700 rounded"
                      title="Подключить Telegram"
                    >
                      <MessageCircle size={18} />
                    </button>
                  )}
                  {channel.platform === 'vk' && (
                    <button
                      onClick={() => openVkModal(channel.id)}
                      className="p-2 text-blue-500 hover:text-blue-400 hover:bg-gray-700 rounded"
                      title="Подключить VK"
                    >
                      🔵
                    </button>
                  )}
                  {channel.platform === 'youtube' && (
                    <button
                      onClick={() => openYoutubeModal(channel.id)}
                      className="p-2 text-red-500 hover:text-red-400 hover:bg-gray-700 rounded"
                      title="Подключить YouTube"
                    >
                      ▶️
                    </button>
                  )}
                  {channel.platform === 'dzen' && (
                    <button
                      onClick={() => openDzenModal(channel.id)}
                      className="p-2 text-yellow-500 hover:text-yellow-400 hover:bg-gray-700 rounded"
                      title="Подключить Dzen"
                    >
                      📰
                    </button>
                  )}
                  <button
                onClick={() => { setManagerChannel({id: channel.id, name: channel.name}); setShowManagerModal(true); }}
                className="p-2 rounded-lg bg-purple-500 bg-opacity-20 text-purple-400 hover:bg-opacity-30 transition-colors"
                title="Настройки канала"
              >
                <Settings size={18} />
              </button>
              <button
                    onClick={() => openScheduleModal(channel.id)}
                    className="p-2 text-gray-400 hover:text-purple-400 hover:bg-gray-700 rounded"
                    title="Расписание публикаций"
                  >
                    <Clock size={18} />
                  </button>
                  <button
                    onClick={() => handleDeleteChannel(channel.id)}
                    className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for creating channel */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6">Создать канал</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">Название</label>
                <input
                  type="text"
                  value={newChannel.name}
                  onChange={(e) => setNewChannel({...newChannel, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  placeholder="AI Новости"
                />
              </div>

              <div>
                <label className="block text-gray-400 text-sm mb-2">Платформа</label>
                <select
                  value={newChannel.platform}
                  onChange={(e) => setNewChannel({...newChannel, platform: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="telegram">📱 Telegram</option>
                  <option value="vk">🔵 VK (ВКонтакте)</option>
                  <option value="youtube">▶️ YouTube Shorts</option>
                  <option value="dzen">📰 Dzen (Дзен)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Язык поиска</label>
                  <select
                    value={newChannel.language_search}
                    onChange={(e) => setNewChannel({...newChannel, language_search: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="en">English</option>
                    <option value="ru">Русский</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-400 text-sm mb-2">Язык публикации</label>
                  <select
                    value={newChannel.language_publish}
                    onChange={(e) => setNewChannel({...newChannel, language_publish: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="ru">Русский</option>
                    <option value="en">English</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-gray-400 text-sm mb-2">Стиль</label>
                <select
                  value={newChannel.style_profile}
                  onChange={(e) => setNewChannel({...newChannel, style_profile: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="minimal">Minimal</option>
                  <option value="techcrunch">TechCrunch</option>
                  <option value="vc">VC.ru</option>
                  <option value="expert">Expert</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-400 text-sm mb-2">Описание</label>
                <textarea
                  value={newChannel.description}
                  onChange={(e) => setNewChannel({...newChannel, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  rows={3}
                  placeholder="Описание канала..."
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCreateChannel}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Создать
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal for Telegram connection */}
      {showTelegramModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <MessageCircle className="mr-2 text-blue-400" />
              Подключить Telegram бота
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">
                  Bot Token от @BotFather
                </label>
                <input
                  type="password"
                  value={telegramForm.bot_token}
                  onChange={(e) => setTelegramForm({...telegramForm, bot_token: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  placeholder="123456:ABC-DEF..."
                />
                <p className="text-xs text-gray-500 mt-1">
                  Получите токен у @BotFather в Telegram
                </p>
              </div>

              <div>
                <label className="block text-gray-400 text-sm mb-2">
                  Chat ID канала (опционально)
                </label>
                <input
                  type="text"
                  value={telegramForm.chat_id}
                  onChange={(e) => setTelegramForm({...telegramForm, chat_id: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  placeholder="@channel_name или -100123456789"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Оставьте пустым для автоматического определения
                </p>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleConnectTelegram}
                disabled={connecting || !telegramForm.bot_token}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {connecting ? 'Подключение...' : 'Подключить'}
              </button>
              <button
                onClick={() => setShowTelegramModal(false)}
                disabled={connecting}
                className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
            {/* Sprint 11: Modal for VK/YouTube/Dzen connection */}
      {showPlatformModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <span className="mr-2">
                {platformType === 'vk' && '🔵'}
                {platformType === 'youtube' && '▶️'}
                {platformType === 'dzen' && '📰'}
              </span>
              Подключить {platformType === 'vk' && 'VK'}
                         {platformType === 'youtube' && 'YouTube'}
                         {platformType === 'dzen' && 'Dzen'}
            </h2>

            {platformType === 'vk' && (
              <>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">VK Group ID</label>
                  <input
                    type="text"
                    value={platformForm.group_id || ''}
                    onChange={(e) => setPlatformForm({...platformForm, group_id: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="-123456789 или my_group"
                  />
                  <p className="text-xs text-gray-500 mt-1">ID группы VK (со знаком минус)</p>
                </div>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">Access Token</label>
                  <input
                    type="password"
                    value={platformForm.access_token || ''}
                    onChange={(e) => setPlatformForm({...platformForm, access_token: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="vk1.a..."
                  />
                  <p className="text-xs text-gray-500 mt-1">Токен с правами wall, groups</p>
                </div>
              </>
            )}

            {platformType === 'youtube' && (
              <>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">YouTube Channel ID</label>
                  <input type="text" value={platformForm.channel_id || ''}
                    onChange={(e) => setPlatformForm({...platformForm, channel_id: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="UC..." />
                </div>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">YouTube API Key</label>
                  <input type="password" value={platformForm.api_key || ''}
                    onChange={(e) => setPlatformForm({...platformForm, api_key: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="AIza..." />
                  <p className="text-xs text-gray-500 mt-1">YouTube Data API v3 key</p>
                </div>
              </>
            )}

            {platformType === 'dzen' && (
              <>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">Dzen Channel ID</label>
                  <input type="text" value={platformForm.channel_id || ''}
                    onChange={(e) => setPlatformForm({...platformForm, channel_id: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="123456" />
                </div>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">Dzen API Key</label>
                  <input type="password" value={platformForm.api_key || ''}
                    onChange={(e) => setPlatformForm({...platformForm, api_key: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="Dzen API key" />
                </div>
              </>
            )}

            <div className="flex gap-3 mt-6">
              <button onClick={handleConnectPlatform} disabled={connecting}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                {connecting ? 'Подключение...' : 'Подключить'}
              </button>
              <button onClick={() => setShowPlatformModal(false)} disabled={connecting}
                className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50">
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

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
                  <p className="text-xs text-gray-500 mt-1">Формат: минута час день месяц день_недели</p>
                </div>

                <div>
                  <label className="block text-gray-400 text-sm mb-2">Быстрые пресеты</label>
                  <div className="grid grid-cols-2 gap-2">
                    {cronPresets.map((p) => (
                      <button
                        key={p.value}
                        onClick={() => setScheduleForm({...scheduleForm, cron_expression: p.value})}
                        className={'px-3 py-2 text-sm rounded-lg border ' + (scheduleForm.cron_expression === p.value ? 'bg-purple-600 border-purple-500 text-white' : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600')}
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
                    <div className="text-xs text-gray-400">Публиковать одобренные посты автоматически</div>
                  </div>
                  <button
                    onClick={() => setScheduleForm({...scheduleForm, auto_publish: !scheduleForm.auto_publish})}
                    className={'relative w-12 h-6 rounded-full transition-colors ' + (scheduleForm.auto_publish ? 'bg-purple-600' : 'bg-gray-600')}
                  >
                    <span className={'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ' + (scheduleForm.auto_publish ? 'translate-x-6' : '')} />
                  </button>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div>
                    <div className="text-white text-sm font-medium">Расписание активно</div>
                    <div className="text-xs text-gray-400">Включить автозапуск пайплайна</div>
                  </div>
                  <button
                    onClick={() => setScheduleForm({...scheduleForm, is_active: !scheduleForm.is_active})}
                    className={'relative w-12 h-6 rounded-full transition-colors ' + (scheduleForm.is_active ? 'bg-green-600' : 'bg-gray-600')}
                  >
                    <span className={'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ' + (scheduleForm.is_active ? 'translate-x-6' : '')} />
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

      {showManagerModal && managerChannel && (
        <ChannelManager
          channelId={managerChannel.id}
          channelName={managerChannel.name}
          onClose={() => { setShowManagerModal(false); setManagerChannel(null); }}
          onSaved={loadChannels}
        />
      )}
    </div>
  );
};



export default Channels;

