import { useState } from 'react';
import { Check, Edit2, Plus, X } from 'lucide-react';

interface StrategyPreviewProps {
  suggestion: any;
  onConfirm: (config: any) => void;
  onCancel: () => void;
}

export default function StrategyPreview({ suggestion, onConfirm, onCancel }: StrategyPreviewProps) {
  const [editing, setEditing] = useState(false);
  const [config, setConfig] = useState({
    sources: suggestion.sources || [],
    publishing_frequency: suggestion.publishing_frequency || '6h',
    publishing_mode: suggestion.publishing_mode || 'approval_required',
  });

  const availableSources = [
    'habr', 'vc', 'techcrunch', 'theverge', 'remanga', 'mangadex', 'readmanga',
    'anilist', 'myanimelist', 'pixabay',
  ];

  const toggleSource = (source: string) => {
    setConfig((prev) => ({
      ...prev,
      sources: prev.sources.includes(source)
        ? prev.sources.filter((s: string) => s !== source)
        : [...prev.sources, source],
    }));
  };

  const handleConfirm = () => {
    onConfirm({
      ...suggestion,
      ...config,
    });
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Стратегия канала</h2>
        <button
          onClick={() => setEditing(!editing)}
          className="flex items-center gap-2 px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded-lg"
        >
          <Edit2 size={14} />
          {editing ? 'Готово' : 'Изменить'}
        </button>
      </div>

      {/* Domain & Topic */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Тематика</h3>
        <div className="flex gap-2">
          <span className="px-3 py-1 bg-blue-900/30 text-blue-400 rounded-lg text-sm">
            {suggestion.domain || 'general'}
          </span>
          <span className="px-3 py-1 bg-purple-900/30 text-purple-400 rounded-lg text-sm">
            {suggestion.topic || 'general_news'}
          </span>
          <span className="px-3 py-1 bg-gray-700 text-gray-300 rounded-lg text-sm">
            Уверенность: {Math.round((suggestion.confidence || 0) * 100)}%
          </span>
        </div>
        {suggestion.subtopics?.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {suggestion.subtopics.map((st: string) => (
              <span key={st} className="px-2 py-0.5 bg-gray-700 text-gray-400 rounded text-xs">
                {st}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Sources */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Источники ({config.sources.length})</h3>
        <div className="flex flex-wrap gap-2 mb-2">
          {config.sources.map((src: string) => (
            <span
              key={src}
              className="flex items-center gap-1 px-3 py-1 bg-green-900/30 text-green-400 rounded-lg text-sm"
            >
              <Check size={14} />
              {src}
              {editing && (
                <button onClick={() => toggleSource(src)} className="ml-1 hover:text-red-400">
                  <X size={14} />
                </button>
              )}
            </span>
          ))}
        </div>
        {editing && (
          <div className="border border-gray-700 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-2">Добавить источник:</p>
            <div className="flex flex-wrap gap-1">
              {availableSources
                .filter((s) => !config.sources.includes(s))
                .map((src) => (
                  <button
                    key={src}
                    onClick={() => toggleSource(src)}
                    className="flex items-center gap-1 px-2 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded text-xs"
                  >
                    <Plus size={12} />
                    {src}
                  </button>
                ))}
            </div>
          </div>
        )}
      </div>

      {/* Content Type & Formatter */}
      <div className="mb-6 grid grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-2">Тип контента</h3>
          <div className="px-3 py-2 bg-gray-700 text-gray-300 rounded-lg text-sm">
            {suggestion.content_type || 'news'}
          </div>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-2">Профиль</h3>
          <div className="px-3 py-2 bg-gray-700 text-gray-300 rounded-lg text-sm">
            {suggestion.profile_key}
          </div>
        </div>
      </div>

      {/* Publishing Settings */}
      <div className="mb-6 grid grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-2">Частота публикаций</h3>
          {editing ? (
            <select
              value={config.publishing_frequency}
              onChange={(e) => setConfig({ ...config, publishing_frequency: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 text-gray-300 rounded-lg text-sm border border-gray-600"
            >
              <option value="30m">Каждые 30 минут</option>
              <option value="1h">Каждый час</option>
              <option value="3h">Каждые 3 часа</option>
              <option value="6h">Каждые 6 часов</option>
              <option value="12h">Каждые 12 часов</option>
              <option value="24h">Раз в день</option>
            </select>
          ) : (
            <div className="px-3 py-2 bg-gray-700 text-gray-300 rounded-lg text-sm">
              {config.publishing_frequency === '30m' && 'Каждые 30 минут'}
              {config.publishing_frequency === '1h' && 'Каждый час'}
              {config.publishing_frequency === '3h' && 'Каждые 3 часа'}
              {config.publishing_frequency === '6h' && 'Каждые 6 часов'}
              {config.publishing_frequency === '12h' && 'Каждые 12 часов'}
              {config.publishing_frequency === '24h' && 'Раз в день'}
            </div>
          )}
        </div>
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-2">Режим публикации</h3>
          {editing ? (
            <select
              value={config.publishing_mode}
              onChange={(e) => setConfig({ ...config, publishing_mode: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 text-gray-300 rounded-lg text-sm border border-gray-600"
            >
              <option value="auto">Автоматический</option>
              <option value="approval_required">Требует подтверждения</option>
              <option value="manual">Ручной</option>
            </select>
          ) : (
            <div className="px-3 py-2 bg-gray-700 text-gray-300 rounded-lg text-sm">
              {config.publishing_mode === 'auto' && '🤖 Автоматический'}
              {config.publishing_mode === 'approval_required' && '👁 Требует подтверждения'}
              {config.publishing_mode === 'manual' && '✋ Ручной'}
            </div>
          )}
        </div>
      </div>

      {/* Reasoning */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Обоснование</h3>
        <div className="px-3 py-2 bg-gray-900 text-gray-400 rounded-lg text-xs">
          {suggestion.reasoning || 'Стратегия подобрана на основе названия и описания канала'}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={onCancel}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg"
        >
          Отмена
        </button>
        <button
          onClick={handleConfirm}
          className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold"
        >
          Создать канал
        </button>
      </div>
    </div>
  );
}