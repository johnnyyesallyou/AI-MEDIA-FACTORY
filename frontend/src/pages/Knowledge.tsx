import React, { useEffect, useState } from 'react';
import { knowledgeAPI } from '../api/client';
import { Brain, Plus, Trash2, TrendingUp, Lightbulb, BookOpen, Target, Filter } from 'lucide-react';

interface Insight {
  id: string;
  category: string;
  title: string;
  description: string;
  confidence_score: number;
  created_at: string;
}

const Knowledge: React.FC = () => {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [newInsight, setNewInsight] = useState({
    category: 'best_topic',
    title: '',
    description: '',
    confidence_score: 0.9
  });

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      const response = await knowledgeAPI.listInsights(
        filterCategory === 'all' ? undefined : filterCategory
      );
      setInsights(response.data);
    } catch (error) {
      console.error('Error loading insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInsight = async () => {
    try {
      await knowledgeAPI.createInsight(newInsight);
      setShowCreateModal(false);
      setNewInsight({
        category: 'best_topic',
        title: '',
        description: '',
        confidence_score: 0.9
      });
      loadInsights();
    } catch (error) {
      console.error('Error creating insight:', error);
      alert('Ошибка создания инсайта');
    }
  };

  const handleDeleteInsight = async (id: string) => {
    if (confirm('Удалить инсайт?')) {
      try {
        await knowledgeAPI.deleteInsight(id);
        loadInsights();
      } catch (error) {
        console.error('Error deleting insight:', error);
      }
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'best_topic': return <Target size={18} className="text-blue-400" />;
      case 'best_headline': return <Lightbulb size={18} className="text-yellow-400" />;
      case 'best_image': return <TrendingUp size={18} className="text-green-400" />;
      case 'best_model': return <Brain size={18} className="text-purple-400" />;
      case 'best_prompt': return <BookOpen size={18} className="text-pink-400" />;
      default: return <Brain size={18} className="text-gray-400" />;
    }
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      best_topic: 'Лучшая тема',
      best_headline: 'Лучший заголовок',
      best_image: 'Лучшее изображение',
      best_model: 'Лучшая модель',
      best_prompt: 'Лучший промпт'
    };
    return labels[category] || category;
  };

  const categories = ['all', 'best_topic', 'best_headline', 'best_image', 'best_model', 'best_prompt'];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Brain size={32} className="mr-3 text-purple-400" />
            Knowledge Base
          </h1>
          <p className="text-gray-400 mt-1">Опыт и инсайты платформы</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus size={20} className="mr-2" />
          Добавить инсайт
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              filterCategory === cat
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
            }`}
          >
            {cat === 'all' ? 'Все' : getCategoryLabel(cat)}
          </button>
        ))}
      </div>

      {/* Insights Grid */}
      {loading ? (
        <div className="text-center text-gray-400 py-12">Загрузка инсайтов...</div>
      ) : insights.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
          <Brain size={48} className="mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold text-white mb-2">Инсайтов пока нет</h3>
          <p className="text-gray-400">Добавьте первый инсайт о работе платформы</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {insights.map((insight) => (
            <div key={insight.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center">
                  {getCategoryIcon(insight.category)}
                  <span className="ml-2 text-sm font-medium text-gray-300">
                    {getCategoryLabel(insight.category)}
                  </span>
                </div>
                <button
                  onClick={() => handleDeleteInsight(insight.id)}
                  className="text-gray-500 hover:text-red-400 transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>

              <h3 className="text-lg font-bold text-white mb-2">{insight.title}</h3>
              <p className="text-gray-400 text-sm mb-4">{insight.description}</p>

              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center text-gray-500">
                  <span>Уверенность:</span>
                  <div className="ml-2 flex items-center">
                    <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-green-500 rounded-full"
                        style={{ width: `${insight.confidence_score * 100}%` }}
                      />
                    </div>
                    <span className="ml-2 text-green-400 font-semibold">
                      {Math.round(insight.confidence_score * 100)}%
                    </span>
                  </div>
                </div>
                <span className="text-gray-500">
                  {new Date(insight.created_at).toLocaleDateString('ru-RU')}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <Plus size={24} className="mr-2" />
              Добавить инсайт
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">Категория</label>
                <select
                  value={newInsight.category}
                  onChange={(e) => setNewInsight({...newInsight, category: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="best_topic">Лучшая тема</option>
                  <option value="best_headline">Лучший заголовок</option>
                  <option value="best_image">Лучшее изображение</option>
                  <option value="best_model">Лучшая модель</option>
                  <option value="best_prompt">Лучший промпт</option>
                </select>
              </div>
              
              <div>
                <label className="block text-gray-400 text-sm mb-2">Название</label>
                <input
                  type="text"
                  value={newInsight.title}
                  onChange={(e) => setNewInsight({...newInsight, title: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  placeholder="Темы по AI Safety показывают высокий CTR"
                />
              </div>
              
              <div>
                <label className="block text-gray-400 text-sm mb-2">Описание</label>
                <textarea
                  value={newInsight.description}
                  onChange={(e) => setNewInsight({...newInsight, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  rows={3}
                  placeholder="Темы по безопасности AI показывают CTR на 40% выше среднего"
                />
              </div>
              
              <div>
                <label className="block text-gray-400 text-sm mb-2">
                  Уверенность: {Math.round(newInsight.confidence_score * 100)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={newInsight.confidence_score}
                  onChange={(e) => setNewInsight({...newInsight, confidence_score: parseFloat(e.target.value)})}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCreateInsight}
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
    </div>
  );
};

export default Knowledge;
