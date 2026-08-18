import React, { useEffect, useState } from 'react';
import { analyticsAPI } from '../api/client';
import { 
  TrendingUp, Eye, MousePointerClick, Users, Award, 
  BarChart3, Calendar, Zap, FileText, Bot, Clock 
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts';

interface Overview {
  total_views: number;
  avg_ctr: number;
  avg_er: number;
  subscribers_growth: number;
}

interface BestPerformer {
  category: string;
  name: string;
  score: number;
  metric_name: string;
}

interface TimeSeriesPoint {
  date: string;
  views: number;
  ctr: number;
}

const Analytics: React.FC = () => {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [bestPerformers, setBestPerformers] = useState<BestPerformer[]>([]);
  const [timeSeries, setTimeSeries] = useState<TimeSeriesPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [overviewRes, performersRes, timeSeriesRes] = await Promise.all([
        analyticsAPI.getOverview(),
        analyticsAPI.getBestPerformers(),
        analyticsAPI.getTimeSeries(7),
      ]);
      setOverview(overviewRes.data);
      setBestPerformers(performersRes.data);
      setTimeSeries(timeSeriesRes.data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getIconForCategory = (category: string) => {
    switch (category) {
      case 'prompt': return <FileText size={18} className="text-purple-400" />;
      case 'llm': return <Bot size={18} className="text-blue-400" />;
      case 'hour': return <Clock size={18} className="text-yellow-400" />;
      case 'topic': return <Zap size={18} className="text-green-400" />;
      case 'image_style': return <Eye size={18} className="text-pink-400" />;
      default: return <Award size={18} className="text-gray-400" />;
    }
  };

  if (loading) {
    return <div className="text-center text-gray-400 py-12">Загрузка аналитики...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-white">Analytics</h1>
        <div className="flex items-center text-gray-400 text-sm">
          <Calendar size={16} className="mr-2" />
          Период: Последние 7 дней
        </div>
      </div>

      {/* Overview Cards */}
      {overview && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-400 text-sm font-medium">Общие просмотры</h3>
              <Eye size={18} className="text-blue-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-1">{overview.total_views.toLocaleString()}</div>
            <div className="text-green-400 text-xs flex items-center">
              <TrendingUp size={12} className="mr-1" /> +12.5% к прошлой неделе
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-400 text-sm font-medium">Средний CTR</h3>
              <MousePointerClick size={18} className="text-purple-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-1">{overview.avg_ctr}%</div>
            <div className="text-green-400 text-xs flex items-center">
              <TrendingUp size={12} className="mr-1" /> +0.8% к прошлой неделе
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-400 text-sm font-medium">Средний ER</h3>
              <BarChart3 size={18} className="text-yellow-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-1">{overview.avg_er}%</div>
            <div className="text-green-400 text-xs flex items-center">
              <TrendingUp size={12} className="mr-1" /> +1.2% к прошлой неделе
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-400 text-sm font-medium">Рост подписчиков</h3>
              <Users size={18} className="text-green-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-1">+{overview.subscribers_growth}</div>
            <div className="text-green-400 text-xs flex items-center">
              <TrendingUp size={12} className="mr-1" /> Отличный рост!
            </div>
          </div>
        </div>
      )}

      {/* Time Series Chart */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
        <h2 className="text-xl font-bold text-white mb-6">Динамика просмотров и CTR</h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timeSeries}>
              <defs>
                <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Area 
                type="monotone" 
                dataKey="views" 
                stroke="#3b82f6" 
                fillOpacity={1} 
                fill="url(#colorViews)" 
                name="Просмотры"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Best Performers */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center mb-6">
          <Award size={24} className="text-yellow-400 mr-3" />
          <h2 className="text-xl font-bold text-white">Лучшие показатели (Best Performers)</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {bestPerformers.map((item, idx) => (
            <div key={idx} className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50 hover:border-gray-600 transition-colors">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  {getIconForCategory(item.category)}
                  <span className="ml-2 text-sm font-medium text-gray-300 capitalize">
                    {item.category.replace('_', ' ')}
                  </span>
                </div>
                <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
                  по метрике {item.metric_name}
                </span>
              </div>
              <div className="text-lg font-bold text-white mb-1">{item.name}</div>
              <div className="text-2xl font-bold text-green-400">{item.score}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Analytics;
