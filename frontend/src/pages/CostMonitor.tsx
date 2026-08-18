import React, { useEffect, useState } from 'react';
import { 
  DollarSign, Cpu, Clock, Zap, TrendingUp, 
  BarChart3, Activity, Server, Database
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line
} from 'recharts';

interface CostBreakdown {
  task: string;
  cost: number;
  duration_minutes: number;
  gpu_usage_percent: number;
}

interface DailyCost {
  date: string;
  total: number;
  research: number;
  writing: number;
  images: number;
}

const CostMonitor: React.FC = () => {
  const [todayCost, setTodayCost] = useState(0);
  const [monthlyCost, setMonthlyCost] = useState(0);
  const [breakdown, setBreakdown] = useState<CostBreakdown[]>([]);
  const [dailyCosts, setDailyCosts] = useState<DailyCost[]>([]);
  const [gpuStats, setGpuStats] = useState({
    usage: 45,
    temperature: 67,
    memory_used: 8.2,
    memory_total: 24
  });

  useEffect(() => {
    // Демо-данные (в реальности - из API)
    const todayBreakdown: CostBreakdown[] = [
      { task: 'Research', cost: 0.12, duration_minutes: 45, gpu_usage_percent: 30 },
      { task: 'Writing', cost: 0.45, duration_minutes: 120, gpu_usage_percent: 65 },
      { task: 'Images', cost: 0.30, duration_minutes: 90, gpu_usage_percent: 85 },
      { task: 'Fact Check', cost: 0.08, duration_minutes: 30, gpu_usage_percent: 25 },
      { task: 'Evaluation', cost: 0.05, duration_minutes: 20, gpu_usage_percent: 20 },
    ];
    
    const dailyData: DailyCost[] = [
      { date: '15.07', total: 0.75, research: 0.10, writing: 0.40, images: 0.25 },
      { date: '16.07', total: 0.82, research: 0.11, writing: 0.43, images: 0.28 },
      { date: '17.07', total: 0.68, research: 0.09, writing: 0.38, images: 0.21 },
      { date: '18.07', total: 0.91, research: 0.13, writing: 0.48, images: 0.30 },
      { date: '19.07', total: 0.87, research: 0.12, writing: 0.45, images: 0.30 },
      { date: '20.07', total: 0.95, research: 0.14, writing: 0.50, images: 0.31 },
      { date: '21.07', total: 0.87, research: 0.12, writing: 0.45, images: 0.30 },
    ];

    setBreakdown(todayBreakdown);
    setDailyCosts(dailyData);
    setTodayCost(todayBreakdown.reduce((acc, item) => acc + item.cost, 0));
    setMonthlyCost(24.56);
  }, []);

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b'];

  const pieData = breakdown.map(item => ({
    name: item.task,
    value: item.cost
  }));

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <DollarSign size={32} className="mr-3 text-green-400" />
            Cost Monitor
          </h1>
          <p className="text-gray-400 mt-1">Мониторинг стоимости и ресурсов</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600">
            Сегодня
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Неделя
          </button>
          <button className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600">
            Месяц
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400 text-sm font-medium">Сегодня</h3>
            <DollarSign size={18} className="text-green-400" />
          </div>
          <div className="text-3xl font-bold text-white mb-1">${todayCost.toFixed(2)}</div>
          <div className="text-green-400 text-xs flex items-center">
            <TrendingUp size={12} className="mr-1" /> -5% к вчера
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400 text-sm font-medium">Этот месяц</h3>
            <BarChart3 size={18} className="text-blue-400" />
          </div>
          <div className="text-3xl font-bold text-white mb-1">${monthlyCost}</div>
          <div className="text-gray-400 text-xs">Прогноз: $26.50</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400 text-sm font-medium">GPU Usage</h3>
            <Cpu size={18} className="text-purple-400" />
          </div>
          <div className="text-3xl font-bold text-white mb-1">{gpuStats.usage}%</div>
          <div className="text-gray-400 text-xs">Temp: {gpuStats.temperature}°C</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400 text-sm font-medium">Время работы</h3>
            <Clock size={18} className="text-yellow-400" />
          </div>
          <div className="text-3xl font-bold text-white mb-1">5h 5m</div>
          <div className="text-gray-400 text-xs">Сегодня</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Daily Cost Trend */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-6">Динамика стоимости (7 дней)</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dailyCosts}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Line type="monotone" dataKey="total" stroke="#10b981" strokeWidth={2} name="Всего" />
                <Line type="monotone" dataKey="writing" stroke="#3b82f6" strokeWidth={2} name="Writing" />
                <Line type="monotone" dataKey="images" stroke="#ec4899" strokeWidth={2} name="Images" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cost Breakdown Pie */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-6">Распределение по задачам</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap justify-center gap-4 mt-4">
            {pieData.map((entry, index) => (
              <div key={entry.name} className="flex items-center text-sm">
                <div 
                  className="w-3 h-3 rounded-full mr-2" 
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="text-gray-400">{entry.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed Breakdown */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-6">Детализация за сегодня</h2>
        <div className="space-y-4">
          {breakdown.map((item, idx) => (
            <div key={item.task} className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  <div 
                    className="w-4 h-4 rounded-full mr-3" 
                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                  />
                  <h3 className="text-lg font-semibold text-white">{item.task}</h3>
                </div>
                <div className="text-2xl font-bold text-green-400">${item.cost.toFixed(2)}</div>
              </div>
              
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <div className="text-gray-500 mb-1">Время</div>
                  <div className="text-white flex items-center">
                    <Clock size={14} className="mr-1" />
                    {item.duration_minutes} мин
                  </div>
                </div>
                <div>
                  <div className="text-gray-500 mb-1">GPU Usage</div>
                  <div className="text-white flex items-center">
                    <Cpu size={14} className="mr-1" />
                    {item.gpu_usage_percent}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-500 mb-1">Стоимость/мин</div>
                  <div className="text-white">
                    ${(item.cost / item.duration_minutes).toFixed(3)}
                  </div>
                </div>
              </div>

              {/* Progress bar for GPU usage */}
              <div className="mt-3">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>GPU нагрузка</span>
                  <span>{item.gpu_usage_percent}%</span>
                </div>
                <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all"
                    style={{ 
                      width: `${item.gpu_usage_percent}%`,
                      backgroundColor: COLORS[idx % COLORS.length]
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Resource Usage */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center mb-4">
            <Server size={20} className="text-blue-400 mr-2" />
            <h3 className="text-lg font-semibold text-white">GPU Memory</h3>
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {gpuStats.memory_used} / {gpuStats.memory_total} GB
          </div>
          <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-500 rounded-full"
              style={{ width: `${(gpuStats.memory_used / gpuStats.memory_total) * 100}%` }}
            />
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center mb-4">
            <Activity size={20} className="text-green-400 mr-2" />
            <h3 className="text-lg font-semibold text-white">Активные задачи</h3>
          </div>
          <div className="text-3xl font-bold text-white mb-2">3</div>
          <div className="text-gray-400 text-sm">Writing, Images, Fact Check</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center mb-4">
            <Database size={20} className="text-purple-400 mr-2" />
            <h3 className="text-lg font-semibold text-white">Сгенерировано</h3>
          </div>
          <div className="text-3xl font-bold text-white mb-2">18</div>
          <div className="text-gray-400 text-sm">постов сегодня</div>
        </div>
      </div>
    </div>
  );
};

export default CostMonitor;
