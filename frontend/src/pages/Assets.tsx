import React, { useEffect, useState } from 'react';
import { assetsAPI } from '../api/client';
import { FolderOpen, Upload, Image, Video, Type, Palette, Cpu, FileJson, Trash2, Download, Search } from 'lucide-react';

interface AssetItem {
  id: string;
  name: string;
  asset_type: string;
  url: string;
  size_kb: number;
  created_at: string;
}

const Assets: React.FC = () => {
  const [assets, setAssets] = useState<AssetItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadAssets();
  }, []);

  const loadAssets = async () => {
    try {
      const typeParam = filterType === 'all' ? undefined : filterType;
      const response = await assetsAPI.list(typeParam);
      setAssets(response.data.items || []);
    } catch (error) {
      console.error('Error loading assets:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'image': return <Image size={18} className="text-blue-400" />;
      case 'video': return <Video size={18} className="text-purple-400" />;
      case 'font': return <Type size={18} className="text-green-400" />;
      case 'logo': return <Palette size={18} className="text-yellow-400" />;
      case 'lora': return <Cpu size={18} className="text-pink-400" />;
      case 'workflow': return <FileJson size={18} className="text-orange-400" />;
      default: return <FolderOpen size={18} className="text-gray-400" />;
    }
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      image: 'Изображение',
      video: 'Видео',
      font: 'Шрифт',
      logo: 'Логотип',
      lora: 'LoRA модель',
      workflow: 'ComfyUI Workflow'
    };
    return labels[type] || type;
  };

  const formatSize = (sizeKb: number) => {
    if (sizeKb >= 1024) {
      return `${(sizeKb / 1024).toFixed(1)} MB`;
    }
    return `${sizeKb} KB`;
  };

  const filteredAssets = assets.filter(asset =>
    asset.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const assetTypes = ['all', 'image', 'video', 'font', 'logo', 'lora', 'workflow'];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <FolderOpen size={32} className="mr-3 text-blue-400" />
            Assets Library
          </h1>
          <p className="text-gray-400 mt-1">Библиотека медиа и ресурсов</p>
        </div>
        <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <Upload size={20} className="mr-2" />
          Загрузить файл
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="flex-1 relative">
          <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Поиск ассетов..."
            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {assetTypes.map((type) => (
          <button
            key={type}
            onClick={() => setFilterType(type)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              filterType === type
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
            }`}
          >
            {type === 'all' ? 'Все' : getTypeLabel(type)}
          </button>
        ))}
      </div>

      {/* Assets Grid */}
      {loading ? (
        <div className="text-center text-gray-400 py-12">Загрузка ассетов...</div>
      ) : filteredAssets.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
          <FolderOpen size={48} className="mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold text-white mb-2">Ассетов не найдено</h3>
          <p className="text-gray-400">Загрузите первый файл в библиотеку</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAssets.map((asset) => (
            <div key={asset.id} className="bg-gray-800 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors overflow-hidden">
              {/* Preview Area */}
              <div className="h-40 bg-gray-900 flex items-center justify-center">
                {asset.asset_type === 'image' ? (
                  <img src={asset.url} alt={asset.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="text-center">
                    {getTypeIcon(asset.asset_type)}
                    <p className="text-gray-500 text-sm mt-2">Preview</p>
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-white truncate">{asset.name}</h3>
                    <div className="flex items-center text-sm text-gray-400 mt-1">
                      {getTypeIcon(asset.asset_type)}
                      <span className="ml-2">{getTypeLabel(asset.asset_type)}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500 mt-3 pt-3 border-t border-gray-700">
                  <span>{formatSize(asset.size_kb)}</span>
                  <span>{new Date(asset.created_at).toLocaleDateString('ru-RU')}</span>
                </div>

                <div className="flex gap-2 mt-3">
                  <button className="flex-1 px-3 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 hover:text-white text-sm flex items-center justify-center">
                    <Download size={14} className="mr-1" />
                    Скачать
                  </button>
                  <button className="px-3 py-2 bg-red-600/20 text-red-400 rounded hover:bg-red-600/30 text-sm">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Assets;
