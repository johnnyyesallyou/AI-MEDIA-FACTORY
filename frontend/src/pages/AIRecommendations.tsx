import React, { useEffect, useState } from 'react';
import { 
  Brain, TrendingUp, Clock, FileText, Bot, Target, 
  CheckCircle, XCircle, Lightbulb, Zap, ArrowRight,
  Filter, Sparkles
} from 'lucide-react';

interface Recommendation {
  id: string;
  category: string;
  title: string;
  description: string;
  metric: string;
  impact: number;
  confidence: number;
  status: 'new' | 'applied' | 'dismissed';
  created_at: string;
}

const AIRecommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Демо-данные (в реальности - из API)
    const demoRecommendations: Recommendation[] = [
      {
        id: '1',
        category: 'content',
        title: 'Оптимальная длина поста',
        description: 'Посты длиной 700–900 символов получают на 18% больше просмотров. Текущий средний размер: 650 символов.',
        metric: '+18% просмотров',
        impact: 85,
        confidence: 92,
        status: 'new',
        created_at: '2026-07-21T10:00:00Z'
      },
      {
        id: '2',
        category: 'timing',
        title: 'Лучшее время публикации',
        description: 'Публикации в 18:30 показывают лучший ER (12.4%). Сейчас вы публикуете в 17:00 и 21:00.',
        metric: '+12.4% ER',
        impact: 78,
        confidence: 88,
        status: 'new',
        created_at: '2026-07-21T09:30:00Z'
      },
      {
        id: '3',
        category: 'prompt',
        title: 'Prompt v12 превосходит v11',
        description: 'Prompt v12 показывает Quality Score на 9% выше, чем v11. Рекомендуется переключиться.',
        metric: '+9% Quality Score',
        impact: 72,
        confidence: 95,
        status: 'new',
        created_at: '2026-07-21T08:15:00Z'
      },
      {
        id: '4',
        category: 'model',
        title: 'GPT-4o для Fact Check',
        description: 'Тесты показали, что GPT-4o дает Fact Score на 15% выше, чем текущая Gemma-27b.',
        metric: '+15% Fact Score',
        impact: 90,
        confidence: 87,
        status: 'new',
        created_at: '2026-07-20T16:45:00Z'
      },
      {
        id: '5',
        category: 'content',
        title: 'Используйте вопросы в заголовках',
        description: 'Заголовки с вопросами получают на 23% больше кликов. Пример: "Что изменит GPT-Red в AI Safety?"',
        metric: '+23% CTR',
        impact: 68,
        confidence: 91,
        status: 'new',
        created_at: '2026-07-20T14:20:00Z'
      },
      {
        id: '6',
        category: 'timing',
        title: 'Избегайте публикаций в выходные',
        description: 'ER в субботу и воскресенье на 34% ниже, чем в будни. Рекомендуется отключить автопубликацию.',
        metric: '-34% ER в выходные',
        impact: 65,
        confidence: 89,
        status: 'new',
        created_at: '2026-07-20T11:00:00Z'
      },
      {
        id: '7',
        category: 'prompt',
        title: 'Добавьте эмодзи в начало поста',
        description: 'Посты с эмодзи в первой строке показывают на 11% выше вовлеченность.',
        metric: '+11% Engagement',
        impact: 55,
        confidence: 84,
        status: 'new',
        created_at: '2026-07-19T15:30:00Z'
      },
      {
        id: '8',
        category: 'model',
        title: 'Qwen3 для Writing',
        description: 'Qwen3-32B генерирует тексты на 20% быстрее, чем текущая модель, с аналогичным качеством.',
        metric: '+20% скорость',
        impact: 70,
        confidence: 93,
        status: 'new',
        created_at: '2026-07-19T10:15:00Z'
      }
    ];

    setRecommendations(demoRecommendations);
    setLoading(false);
  }, []);

  const handleApply = (id: string) => {
    setRecommendations(prev =>
      prev.map(rec => rec.id === id ? { ...rec, status: 'applied' } : rec)
    );
    alert('Рекомендация применена! (В реальности здесь будет вызов API)');
  };

  const handleDismiss = (id: string) => {
    setRecommendations(prev =>
      prev.map(rec => rec.id === id ? { ...rec, status: 'dismissed' } : rec)
    );
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'content': return <FileText size={18} className="text-blue-400" />;
      case 'timing': return <Clock size={18} className="text-yellow-400" />;
      case 'prompt': return <Sparkles size={18} className="text-purple-400" />;
      case 'model': return <Bot size={18} className="text-green-400" />;
      default: return <Lightbulb size={18} className="text-gray-400" />;
    }
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      content: 'Контент',
      timing: 'Время публикации',
      prompt: 'Промпты',
      model: 'Модели'
    };
    return labels[category] || category;
  };

  const getImpactColor = (impact: number) => {
    if (impact >= 80) return 'text-green-400';
    if (impact >= 60) return 'text-yellow-400';
    return 'text-gray-400';
  };

  const filteredRecommendations = filterCategory === 'all'
    ? recommendations
    : recommendations.filter(r => r.category === filterCategory);

  const activeRecommendations = filteredRecommendations.filter(r => r.status === 'new');
  const appliedCount = recommendations.filter(r => r.status === 'applied').length;

  const categories = ['all', 'content', 'timing', 'prompt', 'model'];

  if (loading) {
    return <div className="text-center text-gray-400 py-12">Анализ данных...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Brain size={32} className="mr-3 text-purple-400" />
            AI Recommendations
          </h1>
          <p className="text-gray-400 mt-1">Умные рекомендации на основе анализа данных</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-sm text-gray-400">Применено</div>
            <div className="text-2xl font-bold text-green-400">{appliedCount}</div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-400">Новых</div>
            <div className="text-2xl font-bold text-blue-400">{activeRecommendations.length}</div>
          </div>
        </div>
      </div>

      {/* Summary Card */}
      <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-lg p-6 border border-purple-700/50 mb-8">
        <div className="flex items-start">
          <Sparkles size={24} className="text-purple-400 mr-4 mt-1" />
          <div className="flex-1">
            <h2 className="text-xl font-bold text-white mb-2">AI проанализировал ваши данные</h2>
            <p className="text-gray-300 mb-4">
              На основе {recommendations.length} рекомендаций, система выявила паттерны, которые могут улучшить показатели вашего канала.
              Применение всех рекомендаций может увеличить ER на <span className="text-green-400 font-semibold">~25%</span>.
            </p>
            <div className="flex gap-3">
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center">
                <Zap size={16} className="mr-2" />
                Применить все
              </button>
              <button className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600">
                Подробнее об анализе
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap flex items-center ${
              filterCategory === cat
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
            }`}
          >
            {cat === 'all' ? (
              <>
                <Filter size={14} className="mr-2" />
                Все ({recommendations.length})
              </>
            ) : (
              <>
                {getCategoryIcon(cat)}
                <span className="ml-2">{getCategoryLabel(cat)}</span>
              </>
            )}
          </button>
        ))}
      </div>

      {/* Recommendations List */}
      {activeRecommendations.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
          <CheckCircle size={48} className="mx-auto mb-4 text-green-400" />
          <h3 className="text-xl font-semibold text-white mb-2">Все рекомендации применены!</h3>
          <p className="text-gray-400">Система продолжит анализ и предложит новые улучшения</p>
        </div>
      ) : (
        <div className="space-y-4">
          {activeRecommendations.map((rec) => (
            <div key={rec.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start flex-1">
                  <div className="mr-4 mt-1">
                    {getCategoryIcon(rec.category)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-bold text-white">{rec.title}</h3>
                      <span className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                        {getCategoryLabel(rec.category)}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm mb-3">{rec.description}</p>
                    
                    <div className="flex items-center gap-6 text-sm">
                      <div className="flex items-center">
                        <Target size={14} className="mr-2 text-green-400" />
                        <span className="text-gray-400">Эффект:</span>
                        <span className={`ml-2 font-semibold ${getImpactColor(rec.impact)}`}>
                          {rec.metric}
                        </span>
                      </div>
                      <div className="flex items-center">
                        <Brain size={14} className="mr-2 text-blue-400" />
                        <span className="text-gray-400">Уверенность:</span>
                        <span className="ml-2 text-blue-400 font-semibold">{rec.confidence}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Impact Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Приоритет</span>
                  <span>{rec.impact}%</span>
                </div>
                <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all"
                    style={{ 
                      width: `${rec.impact}%`,
                      backgroundColor: rec.impact >= 80 ? '#10b981' : rec.impact >= 60 ? '#f59e0b' : '#6b7280'
                    }}
                  />
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-gray-700">
                <button
                  onClick={() => handleApply(rec.id)}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center transition-colors"
                >
                  <CheckCircle size={16} className="mr-2" />
                  Применить
                </button>
                <button
                  onClick={() => handleDismiss(rec.id)}
                  className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 flex items-center justify-center transition-colors"
                >
                  <XCircle size={16} className="mr-2" />
                  Отклонить
                </button>
                <button className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 flex items-center justify-center transition-colors">
                  Подробнее
                  <ArrowRight size={16} className="ml-2" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Applied Recommendations */}
      {appliedCount > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <CheckCircle size={20} className="mr-2 text-green-400" />
            Примененные рекомендации ({appliedCount})
          </h2>
          <div className="space-y-3">
            {recommendations.filter(r => r.status === 'applied').map((rec) => (
              <div key={rec.id} className="bg-gray-800/50 rounded-lg p-4 border border-green-700/30 opacity-75">
                <div className="flex items-center">
                  <CheckCircle size={18} className="text-green-400 mr-3" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-white">{rec.title}</h3>
                    <p className="text-sm text-gray-400">{rec.metric}</p>
                  </div>
                  <span className="text-xs text-gray-500">
                    Применено {new Date().toLocaleDateString('ru-RU')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIRecommendations;
