import React, { useEffect, useState } from 'react';
import { dashboardAPI, channelsAPI, aiAPI } from '../api/client';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [channels, setChannels] = useState<any[]>([]);
  const [aiRouting, setAiRouting] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, healthRes, channelsRes, aiRes] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getHealth(),
        channelsAPI.list(),
        aiAPI.getRouting(),
      ]);
      setStats(statsRes.data);
      setHealth(healthRes.data);
      setChannels(channelsRes.data.channels || []);
      setAiRouting(aiRes.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  };

  const statCards = stats ? [
    { label: 'Новости за сутки', value: stats.news_found, sub: `Выбрано: ${stats.news_selected}` },
    { label: 'Постов создано', value: stats.posts_created, sub: `Опубликовано: ${stats.posts_published}` },
    { label: 'Quality Score', value: stats.avg_quality_score || 0, sub: 'из 100' },
    { label: 'Fact Score', value: stats.avg_fact_score || 0, sub: 'из 100' },
    { label: 'Просмотры', value: stats.total_views?.toLocaleString() || 0, sub: `ER: ${stats.total_er}%` },
    { label: 'Ожидают проверки', value: stats.drafts_pending, sub: `Ошибок: ${stats.errors_count}` },
  ] : [];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <button
          onClick={loadData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Обновить
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {statCards.map((card, idx) => (
          <div key={idx} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-gray-400 text-sm mb-2">{card.label}</h3>
            <div className="text-3xl font-bold text-white mb-1">{card.value}</div>
            <div className="text-green-400 text-xs">{card.sub}</div>
          </div>
        ))}
      </div>

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
        <h2 className="text-xl font-bold text-white mb-4">System Health</h2>
        {health && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(health.services || {}).map(([name, service]: [string, any]) => (
              <div key={name} className="bg-gray-700 rounded-lg p-4">
                <div className="font-semibold text-white mb-2">{name}</div>
                <span className={`px-2 py-1 rounded text-xs ${
                  service.status === 'OK' ? 'bg-green-500' : 'bg-red-500'
                }`}>
                  {service.status}
                </span>
                {service.latency_ms && (
                  <div className="text-gray-400 text-xs mt-2">{service.latency_ms}ms</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
        <h2 className="text-xl font-bold text-white mb-4">Channels</h2>
        {channels.length === 0 ? (
          <p className="text-gray-400">Каналов пока нет</p>
        ) : (
          <div className="space-y-3">
            {channels.map((channel: any) => (
              <div key={channel.id} className="bg-gray-700 rounded-lg p-4 flex justify-between items-center">
                <div>
                  <h4 className="font-semibold text-white">{channel.name}</h4>
                  <p className="text-gray-400 text-sm">
                    {channel.platform} • {channel.language_search} → {channel.language_publish}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded text-xs ${
                  channel.is_connected ? 'bg-green-500' : 'bg-red-500'
                }`}>
                  {channel.is_connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">AI Models Routing</h2>
        {aiRouting && (
          <div className="space-y-3">
            {Object.entries(aiRouting).map(([task, config]: [string, any]) => (
              <div key={task} className="bg-gray-700 rounded-lg p-4">
                <div className="font-semibold text-white capitalize mb-1">
                  {task.replace('_', ' ')}
                </div>
                <div className="text-gray-400 text-sm">
                  Модель: <span className="text-blue-400">{config.current_model_id}</span> | 
                  Temp: {config.temperature}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
