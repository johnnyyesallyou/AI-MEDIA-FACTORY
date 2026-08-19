import React, { useEffect, useState } from 'react';
import { contentAPI } from '../api/client';
import { FileText, CheckCircle, XCircle, Eye, Clock, Check, X, ExternalLink, Edit2, Send, MessageCircle } from 'lucide-react';

interface ContentItem {
  id: string;
  channel_id?: string;
  source_url: string;
  headline: string;
  status: string;
  prompt_version?: string;
  draft_text?: string;
  fact_score?: number;
  quality_score?: number;
  telegram_message_id?: string;
  created_at: string;
  updated_at: string;
}

const Content: React.FC = () => {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [editingItem, setEditingItem] = useState<ContentItem | null>(null);
  const [editForm, setEditForm] = useState({ headline: '', draft_text: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadContent();
  }, [activeFilter]);

  const loadContent = async () => {
    setLoading(true);
    try {
      const statusParam = activeFilter === 'all' ? undefined : activeFilter;
      const response = await contentAPI.list(statusParam);
      setItems(response.data.items || []);
    } catch (error) {
      console.error('Error loading content:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (id: string, newStatus: string) => {
    if (!confirm(`Изменить статус на "${newStatus}"?`)) return;
    try {
      await contentAPI.updateStatus(id, newStatus);
      loadContent();
      alert('Статус обновлен!');
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Ошибка при обновлении статуса');
    }
  };

  const openEditModal = (item: ContentItem) => {
    setEditingItem(item);
    setEditForm({ headline: item.headline, draft_text: item.draft_text || '' });
  };

  const handleSaveEdit = async () => {
    if (!editingItem) return;
    setSaving(true);
    try {
      await contentAPI.updateStatus(editingItem.id, 'draft');
      alert('Пост сохранен как черновик');
      setEditingItem(null);
      loadContent();
    } catch (error) {
      alert('Ошибка сохранения');
    } finally {
      setSaving(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      research: 'bg-gray-600 text-gray-200',
      brief: 'bg-blue-600 text-white',
      draft: 'bg-yellow-600 text-white',
      review: 'bg-purple-600 text-white',
      approved: 'bg-green-500 text-white',
      scheduled: 'bg-indigo-600 text-white',
      published: 'bg-green-700 text-white',
      rejected: 'bg-red-600 text-white',
    };
    const labels: Record<string, string> = {
      research: 'Research',
      brief: 'Brief',
      draft: 'Черновик',
      review: 'На проверке',
      approved: 'Одобрено',
      scheduled: 'Запланировано',
      published: 'Опубликовано',
      rejected: 'Отклонено',
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-semibold ${styles[status] || 'bg-gray-600'}`}>
        {labels[status] || status}
      </span>
    );
  };

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-500';
    if (score >= 90) return 'text-green-400';
    if (score >= 80) return 'text-yellow-400';
    return 'text-red-400';
  };

  const filters = [
    { value: 'all', label: 'Все' },
    { value: 'approved', label: 'Одобрено' },
    { value: 'review', label: 'На проверке' },
    { value: 'draft', label: 'Черновики' },
    { value: 'published', label: 'Опубликовано' },
    { value: 'rejected', label: 'Отклонено' },
  ];

  return (
    <div className="relative">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-white">Content Management</h1>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {filters.map((filter) => (
          <button
            key={filter.value}
            onClick={() => setActiveFilter(filter.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeFilter === filter.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* Content List */}
      {loading ? (
        <div className="text-center text-gray-400 py-12">Загрузка контента...</div>
      ) : items.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
          <FileText size={48} className="mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold text-white mb-2">Контент не найден</h3>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <div key={item.id} className="bg-gray-800 rounded-lg p-5 border border-gray-700 hover:border-gray-600 transition-colors">
              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                {/* Main Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2 flex-wrap">
                    {getStatusBadge(item.status)}
                    {item.channel_id && (
                      <span className="text-xs text-blue-300 bg-blue-900/30 px-2 py-1 rounded border border-blue-800">
                        Channel: {item.channel_id.slice(0, 8)}...
                      </span>
                    )}
                    {item.telegram_message_id && (
                      <span className="text-xs text-green-300 bg-green-900/30 px-2 py-1 rounded border border-green-800">
                        <MessageCircle size={12} className="inline mr-1" />
                        TG ID: {item.telegram_message_id}
                      </span>
                    )}
                  </div>

                  <h3 className="text-lg font-semibold text-white mb-2">{item.headline}</h3>

                  <div className="flex items-center gap-4 text-sm text-gray-400 mb-3">
                    <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="flex items-center hover:text-blue-400 transition-colors">
                      <ExternalLink size={14} className="mr-1" /> Источник
                    </a>
                    <span className="flex items-center">
                      <Clock size={14} className="mr-1" />
                      {new Date(item.created_at).toLocaleString('ru-RU')}
                    </span>
                  </div>

                  {item.draft_text && (
                    <div className="text-gray-300 text-sm bg-gray-900/50 p-3 rounded border border-gray-700/50 whitespace-pre-wrap">
                      {item.draft_text}
                    </div>
                  )}
                </div>

                {/* Scores & Actions - ИСПРАВЛЕНО */}
                <div className="flex items-center gap-3 mt-4 lg:mt-0">
                  <div className="flex flex-col items-end gap-2">
                    <div className="text-right">
                      <div className="text-xs text-gray-500 mb-1">Fact Score</div>
                      <div className={`text-xl font-bold ${getScoreColor(item.fact_score)}`}>{item.fact_score ?? '-'}</div>
                    </div>

                    <div className="text-right">
                      <div className="text-xs text-gray-500 mb-1">Quality</div>
                      <div className={`text-xl font-bold ${getScoreColor(item.quality_score)}`}>{item.quality_score ?? '-'}</div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 border-l border-gray-700 pl-3 ml-2">
                    {/* Кнопка Edit - всегда доступна */}
                    <button 
                      onClick={() => openEditModal(item)} 
                      className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors" 
                      title="Редактировать"
                    >
                      <Edit2 size={18} />
                    </button>
                    
                    {/* Кнопки Approve/Reject - для review и draft */}
                    {(item.status === 'review' || item.status === 'draft') && (
                      <>
                        <button 
                          onClick={() => handleStatusChange(item.id, 'approved')} 
                          className="p-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors" 
                          title="Одобрить"
                        >
                          <Check size={18} />
                        </button>
                        <button 
                          onClick={() => handleStatusChange(item.id, 'rejected')} 
                          className="p-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors" 
                          title="Отклонить"
                        >
                          <X size={18} />
                        </button>
                      </>
                    )}
                    
                    {/* Кнопка Publish - для approved */}
                    {item.status === 'approved' && (
                      <button 
                        onClick={() => handleStatusChange(item.id, 'published')} 
                        className="p-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors" 
                        title="Опубликовать"
                      >
                        <Send size={18} />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit Modal */}
      {editingItem && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl border border-gray-700 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold text-white mb-4">Редактирование поста</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">Заголовок</label>
                <input
                  type="text"
                  value={editForm.headline}
                  onChange={(e) => setEditForm({...editForm, headline: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-gray-400 text-sm mb-2">Текст поста</label>
                <textarea
                  value={editForm.draft_text}
                  onChange={(e) => setEditForm({...editForm, draft_text: e.target.value})}
                  rows={10}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500 font-mono text-sm"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleSaveEdit}
                disabled={saving}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? 'Сохранение...' : 'Сохранить как черновик'}
              </button>
              <button
                onClick={() => setEditingItem(null)}
                disabled={saving}
                className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50"
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

export default Content;
