import React, { useEffect, useState } from 'react';
import { integrationsAPI } from '../api/client';
import { Link2, CheckCircle, XCircle, AlertCircle, RefreshCw, Settings, ExternalLink } from 'lucide-react';

interface IntegrationItem {
  id: string;
  name: string;
  category: string;
  status: string;
  last_checked: string;
  details: string;
}

const Integrations: React.FC = () => {
  const [integrations, setIntegrations] = useState<IntegrationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkingId, setCheckingId] = useState<string | null>(null);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      const response = await integrationsAPI.list();
      setIntegrations(response.data.items || []);
    } catch (error) {
      console.error('Error loading integrations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheck = async (id: string) => {
    setCheckingId(id);
    try {
      const response = await integrationsAPI.check(id);
      // Обновляем конкретную интеграцию в списке
      setIntegrations(prev =>
        prev.map(item => item.id === id ? response.data : item)
      );
    } catch (error) {
      console.error('Error checking integration:', error);
      alert('Ошибка проверки подключения');
    } finally {
      setCheckingId(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircle size={20} className="text-green-400" />;
      case 'error': return <XCircle size={20} className="text-red-400" />;
      case 'checking': return <RefreshCw size={20} className="text-yellow-400 animate-spin" />;
      default: return <AlertCircle size={20} className="text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      connected: 'bg-green-500/20 text-green-400 border-green-500/30',
      error: 'bg-red-500/20 text-red-400 border-red-500/30',
      checking: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      disconnected: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    };
    const labels: Record<string, string> = {
      connected: 'Подключено',
      error: 'Ошибка',
      checking: 'Проверка...',
      disconnected: 'Отключено',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[status] || styles.disconnected}`}>
        {labels[status] || status}
      </span>
    );
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      platform: 'Платформы',
      ai_model: 'AI Модели',
      infrastructure: 'Инфраструктура',
    };
    return labels[category] || category;
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'platform': return <ExternalLink size={18} className="text-blue-400" />;
      case 'ai_model': return <Settings size={18} className="text-purple-400" />;
      case 'infrastructure': return <Link2 size={18} className="text-green-400" />;
      default: return <Link2 size={18} className="text-gray-400" />;
    }
  };

  // Группируем по категориям
  const groupedIntegrations = integrations.reduce((acc, item) => {
    if (!acc[item.category]) acc[item.category] = [];
    acc[item.category].push(item);
    return acc;
  }, {} as Record<string, IntegrationItem[]>);

  if (loading) {
    return <div className="text-center text-gray-400 py-12">Загрузка интеграций...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Link2 size={32} className="mr-3 text-green-400" />
            Integrations
          </h1>
          <p className="text-gray-400 mt-1">Все подключения и их статусы</p>
        </div>
        <button
          onClick={loadIntegrations}
          className="flex items-center px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
        >
          <RefreshCw size={18} className="mr-2" />
          Обновить все
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Всего подключений</div>
          <div className="text-2xl font-bold text-white">{integrations.length}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Активных</div>
          <div className="text-2xl font-bold text-green-400">
            {integrations.filter(i => i.status === 'connected').length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">С ошибками</div>
          <div className="text-2xl font-bold text-red-400">
            {integrations.filter(i => i.status === 'error').length}
          </div>
        </div>
      </div>

      {/* Groups */}
      {Object.entries(groupedIntegrations).map(([category, items]) => (
        <div key={category} className="mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            {getCategoryIcon(category)}
            <span className="ml-2">{getCategoryLabel(category)}</span>
            <span className="ml-3 text-sm text-gray-500 font-normal">({items.length})</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {items.map((item) => (
              <div key={item.id} className="bg-gray-800 rounded-lg p-5 border border-gray-700 hover:border-gray-600 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center">
                    <h3 className="text-lg font-semibold text-white">{item.name}</h3>
                  </div>
                  {getStatusIcon(item.status)}
                </div>

                <div className="mb-3">
                  {getStatusBadge(item.status)}
                </div>

                {item.details && (
                  <p className="text-sm text-gray-400 mb-3">{item.details}</p>
                )}

                <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-700">
                  <span>
                    Проверено: {new Date(item.last_checked).toLocaleString('ru-RU')}
                  </span>
                  <button
                    onClick={() => handleCheck(item.id)}
                    disabled={checkingId === item.id}
                    className="flex items-center px-3 py-1 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 hover:text-white disabled:opacity-50 transition-colors"
                  >
                    {checkingId === item.id ? (
                      <RefreshCw size={12} className="mr-1 animate-spin" />
                    ) : (
                      <RefreshCw size={12} className="mr-1" />
                    )}
                    Проверить
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default Integrations;
