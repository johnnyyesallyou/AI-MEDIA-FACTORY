import React, { useEffect, useState } from 'react';
import { aiAPI, aiAPISafe } from '../api/client';
import { Bot, Cpu, Save, RefreshCw, AlertTriangle } from 'lucide-react';

interface RoutingConfig {
  current_model_id: string;
  fallback_model_id: string;
  temperature: number;
}

interface ModelInfo {
  id: string;
  name: string;
  provider: string;
}

const AIModels: React.FC = () => {
  const [routing, setRouting] = useState<Record<string, RoutingConfig>>({});
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [isMockMode, setIsMockMode] = useState(false);
  const [saving, setSaving] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [routingRes, modelsRes] = await Promise.all([
        aiAPISafe.getRouting(),
        aiAPISafe.listModels(),
      ]);
      setRouting(routingRes.data);
      setModels(modelsRes.data);
    } catch (error) {
      console.error('Error loading AI data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleModelChange = async (taskName: string, newModelId: string) => {
    setSaving(taskName);
    try {
      // Находим текущую температуру, чтобы не сбрасывать её
      const currentTemp = routing[taskName]?.temperature || 0.7;
      
      await aiAPI.updateRouting({
        task_name: taskName,
        model_id: newModelId,
        temperature: currentTemp
      });
      
      // Обновляем локальное состояние
      setRouting(prev => ({
        ...prev,
        [taskName]: { ...prev[taskName], current_model_id: newModelId }
      }));
    } catch (error) {
      console.error('Error updating routing:', error);
      alert('Ошибка при смене модели');
    } finally {
      setSaving(null);
    }
  };

  const handleTempChange = async (taskName: string, newTemp: number) => {
    setSaving(taskName);
    try {
      const currentModel = routing[taskName]?.current_model_id;
      
      await aiAPI.updateRouting({
        task_name: taskName,
        model_id: currentModel,
        temperature: newTemp
      });
      
      setRouting(prev => ({
        ...prev,
        [taskName]: { ...prev[taskName], temperature: newTemp }
      }));
    } catch (error) {
      console.error('Error updating temperature:', error);
    } finally {
      setSaving(null);
    }
  };

  const taskLabels: Record<string, string> = {
    research: 'Research (Поиск и анализ)',
    writing: 'Writing (Генерация текста)',
    fact_check: 'Fact Checker (Проверка фактов)',
    evaluator: 'Evaluator (Оценка качества)'
  };

  const taskDescriptions: Record<string, string> = {
    research: 'Низкая температура для точного извлечения фактов',
    writing: 'Средняя температура для креативности в рамках фактов',
    fact_check: 'Очень низкая температура для строгой логики',
    evaluator: 'Низкая температура для объективной оценки'
  };

  if (loading) {
    return <div className="text-center text-gray-400 py-12">Загрузка конфигурации AI...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-white">AI Models Routing</h1>
        <button 
          onClick={loadData}
          className="flex items-center px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
        >
          <RefreshCw size={18} className="mr-2" />
          Обновить
        </button>
      </div>

      <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-4 mb-6 flex items-start">
        <AlertTriangle size={20} className="text-blue-400 mr-3 mt-0.5" />
        <div className="text-sm text-blue-200">
          <strong>Внимание:</strong> Изменения применяются мгновенно и влияют на все новые генерации. 
          Убедитесь, что выбранная модель доступна в вашем Ollama или API провайдере.
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {Object.entries(routing).map(([task, config]) => (
          <div key={task} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center">
                  <Cpu size={20} className="mr-2 text-blue-400" />
                  {taskLabels[task] || task}
                </h3>
                <p className="text-gray-400 text-sm mt-1">{taskDescriptions[task]}</p>
              </div>
              {saving === task && (
                <span className="text-yellow-400 text-sm flex items-center">
                  <RefreshCw size={14} className="mr-1 animate-spin" />
                  Сохранение...
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Выбор модели */}
              <div>
                <label className="block text-gray-400 text-sm mb-2">Основная модель</label>
                <select
                  value={config.current_model_id}
                  onChange={(e) => handleModelChange(task, e.target.value)}
                  disabled={saving === task}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500 disabled:opacity-50"
                >
                  {models.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.name} ({model.provider})
                    </option>
                  ))}
                </select>
                {config.fallback_model_id && (
                  <p className="text-xs text-gray-500 mt-2">
                    Резервная: <span className="text-gray-400">{config.fallback_model_id}</span>
                  </p>
                )}
              </div>

              {/* Настройка температуры */}
              <div>
                <label className="block text-gray-400 text-sm mb-2">
                  Температура: <span className="text-white font-bold">{config.temperature}</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={config.temperature}
                  onChange={(e) => handleTempChange(task, parseFloat(e.target.value))}
                  disabled={saving === task}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Точно (0.0)</span>
                  <span>Креативно (1.0)</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AIModels;
