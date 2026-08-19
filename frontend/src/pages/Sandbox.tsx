import React, { useEffect, useState } from 'react';
import { 
  FlaskConical, Play, CheckCircle, XCircle, Clock, 
  TrendingUp, TrendingDown, Minus, Eye, Trash2,
  Plus, Loader2, BarChart3, ArrowRight, AlertTriangle
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend
} from 'recharts';

interface SandboxTest {
  id: string;
  name: string;
  type: string;
  status: 'running' | 'completed' | 'failed' | 'pending';
  progress: number;
  total_tests: number;
  completed_tests: number;
  created_at: string;
  metrics?: {
    quality_score: { before: number; after: number };
    fact_score: { before: number; after: number };
    engagement: { before: number; after: number };
    speed: { before: number; after: number };
  };
  verdict?: 'better' | 'worse' | 'same';
}

const Sandbox: React.FC = () => {
  const [tests, setTests] = useState<SandboxTest[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTest, setNewTest] = useState({
    name: '',
    type: 'prompt',
    description: ''
  });

  useEffect(() => {
    // Демо-данные
    const demoTests: SandboxTest[] = [
      {
        id: '1',
        name: 'Prompt v8 vs Production',
        type: 'prompt',
        status: 'completed',
        progress: 100,
        total_tests: 10,
        completed_tests: 10,
        created_at: '2026-07-21T08:00:00Z',
        metrics: {
          quality_score: { before: 85, after: 92 },
          fact_score: { before: 88, after: 91 },
          engagement: { before: 7.2, after: 8.9 },
          speed: { before: 45, after: 42 }
        },
        verdict: 'better'
      },
      {
        id: '2',
        name: 'GPT-4o for Fact Check',
        type: 'model',
        status: 'completed',
        progress: 100,
        total_tests: 10,
        completed_tests: 10,
        created_at: '2026-07-20T14:30:00Z',
        metrics: {
          quality_score: { before: 87, after: 89 },
          fact_score: { before: 82, after: 95 },
          engagement: { before: 8.1, after: 8.3 },
          speed: { before: 38, after: 52 }
        },
        verdict: 'better'
      },
      {
        id: '3',
        name: 'New Image Style: Cyberpunk',
        type: 'image',
        status: 'running',
        progress: 60,
        total_tests: 10,
        completed_tests: 6,
        created_at: '2026-07-21T10:15:00Z'
      },
      {
        id: '4',
        name: 'Qwen3-72B for Writing',
        type: 'model',
        status: 'pending',
        progress: 0,
        total_tests: 10,
        completed_tests: 0,
        created_at: '2026-07-21T11:00:00Z'
      }
    ];

    setTests(demoTests);
  }, []);

  const handleCreateTest = () => {
    const newTestObj: SandboxTest = {
      id: String(tests.length + 1),
      name: newTest.name,
      type: newTest.type,
      status: 'running',
      progress: 0,
      total_tests: 10,
      completed_tests: 0,
      created_at: new Date().toISOString()
    };
    
    setTests([newTestObj, ...tests]);
    setShowCreateModal(false);
    setNewTest({ name: '', type: 'prompt', description: '' });
    
    // Симуляция прогресса
    simulateProgress(newTestObj.id);
  };

  const simulateProgress = (testId: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setTests(prev =>
        prev.map(test =>
          test.id === testId
            ? { ...test, progress, completed_tests: Math.floor(progress / 10) }
            : test
        )
      );
      
      if (progress >= 100) {
        clearInterval(interval);
        setTests(prev =>
          prev.map(test =>
            test.id === testId
              ? {
                  ...test,
                  status: 'completed',
                  verdict: 'better',
                  metrics: {
                    quality_score: { before: 85, after: 90 },
                    fact_score: { before: 87, after: 92 },
                    engagement: { before: 7.5, after: 8.8 },
                    speed: { before: 40, after: 38 }
                  }
                }
              : test
          )
        );
      }
    }, 1000);
  };

  const handleApply = (testId: string) => {
    alert('Изменения применены в production! (В реальности здесь будет вызов API)');
    setTests(prev => prev.filter(t => t.id !== testId));
  };

  const handleReject = (testId: string) => {
    setTests(prev => prev.filter(t => t.id !== testId));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Loader2 size={18} className="text-blue-400 animate-spin" />;
      case 'completed': return <CheckCircle size={18} className="text-green-400" />;
      case 'failed': return <XCircle size={18} className="text-red-400" />;
      default: return <Clock size={18} className="text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      running: 'bg-blue-500/20 text-blue-400',
      completed: 'bg-green-500/20 text-green-400',
      failed: 'bg-red-500/20 text-red-400',
      pending: 'bg-gray-500/20 text-gray-400',
    };
    const labels: Record<string, string> = {
      running: 'Выполняется',
      completed: 'Завершено',
      failed: 'Ошибка',
      pending: 'Ожидает',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const getVerdictBadge = (verdict?: string) => {
    if (!verdict) return null;
    const styles: Record<string, string> = {
      better: 'bg-green-500/20 text-green-400 border-green-500/30',
      worse: 'bg-red-500/20 text-red-400 border-red-500/30',
      same: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    };
    const icons: Record<string, React.ReactNode> = {
      better: <TrendingUp size={14} className="mr-1" />,
      worse: <TrendingDown size={14} className="mr-1" />,
      same: <Minus size={14} className="mr-1" />,
    };
    const labels: Record<string, string> = {
      better: 'Лучше production',
      worse: 'Хуже production',
      same: 'Без изменений',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium border flex items-center ${styles[verdict]}`}>
        {icons[verdict]}
        {labels[verdict]}
      </span>
    );
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      prompt: 'Промпт',
      model: 'Модель',
      image: 'Изображение',
      workflow: 'Workflow'
    };
    return labels[type] || type;
  };

  const runningTests = tests.filter(t => t.status === 'running');
  const completedTests = tests.filter(t => t.status === 'completed');
  const pendingTests = tests.filter(t => t.status === 'pending');

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <FlaskConical size={32} className="mr-3 text-purple-400" />
            Sandbox
          </h1>
          <p className="text-gray-400 mt-1">Тестирование изменений перед production</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          <Plus size={20} className="mr-2" />
          Новый тест
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Активных тестов</div>
          <div className="text-2xl font-bold text-blue-400">{runningTests.length}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Завершено</div>
          <div className="text-2xl font-bold text-green-400">{completedTests.length}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Ожидает</div>
          <div className="text-2xl font-bold text-gray-400">{pendingTests.length}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Улучшений</div>
          <div className="text-2xl font-bold text-purple-400">
            {completedTests.filter(t => t.verdict === 'better').length}
          </div>
        </div>
      </div>

      {/* Running Tests */}
      {runningTests.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Loader2 size={20} className="mr-2 text-blue-400 animate-spin" />
            Выполняется ({runningTests.length})
          </h2>
          <div className="space-y-4">
            {runningTests.map((test) => (
              <div key={test.id} className="bg-gray-800 rounded-lg p-6 border border-blue-700/50">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-white">{test.name}</h3>
                    <p className="text-sm text-gray-400">Тип: {getTypeLabel(test.type)}</p>
                  </div>
                  {getStatusBadge(test.status)}
                </div>
                
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-400">Прогресс</span>
                    <span className="text-white font-semibold">{test.progress}%</span>
                  </div>
                  <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 rounded-full transition-all duration-500"
                      style={{ width: `${test.progress}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>Тест {test.completed_tests} из {test.total_tests}</span>
                    <span>Осталось: ~{(test.total_tests - test.completed_tests) * 10}с</span>
                  </div>
                </div>

                <div className="bg-blue-900/20 border border-blue-700/30 rounded-lg p-3 flex items-start">
                  <AlertTriangle size={16} className="text-blue-400 mr-2 mt-0.5" />
                  <p className="text-sm text-blue-200">
                    Тестирование в процессе. Система генерирует тестовые посты и оценивает их качество.
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed Tests with Results */}
      {completedTests.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <CheckCircle size={20} className="mr-2 text-green-400" />
            Результаты тестов ({completedTests.length})
          </h2>
          <div className="space-y-6">
            {completedTests.map((test) => (
              <div key={test.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-white">{test.name}</h3>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-sm text-gray-400">Тип: {getTypeLabel(test.type)}</span>
                      {getVerdictBadge(test.verdict)}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {test.verdict === 'better' && (
                      <button
                        onClick={() => handleApply(test.id)}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center"
                      >
                        <CheckCircle size={16} className="mr-2" />
                        Применить
                      </button>
                    )}
                    <button
                      onClick={() => handleReject(test.id)}
                      className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 flex items-center"
                    >
                      <XCircle size={16} className="mr-2" />
                      Отклонить
                    </button>
                  </div>
                </div>

                {test.metrics && (
                  <>
                    {/* Metrics Comparison */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50">
                        <div className="text-sm text-gray-400 mb-2">Quality Score</div>
                        <div className="flex items-end gap-2">
                          <div className="text-2xl font-bold text-gray-500">{test.metrics.quality_score.before}</div>
                          <ArrowRight size={16} className="text-gray-600 mb-1" />
                          <div className={`text-2xl font-bold ${
                            test.metrics.quality_score.after > test.metrics.quality_score.before 
                              ? 'text-green-400' 
                              : test.metrics.quality_score.after < test.metrics.quality_score.before 
                              ? 'text-red-400' 
                              : 'text-gray-400'
                          }`}>
                            {test.metrics.quality_score.after}
                          </div>
                        </div>
                        <div className={`text-xs mt-1 ${
                          test.metrics.quality_score.after > test.metrics.quality_score.before 
                            ? 'text-green-400' 
                            : 'text-red-400'
                        }`}>
                          {test.metrics.quality_score.after > test.metrics.quality_score.before ? '+' : ''}
                          {test.metrics.quality_score.after - test.metrics.quality_score.before}
                        </div>
                      </div>

                      <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50">
                        <div className="text-sm text-gray-400 mb-2">Fact Score</div>
                        <div className="flex items-end gap-2">
                          <div className="text-2xl font-bold text-gray-500">{test.metrics.fact_score.before}</div>
                          <ArrowRight size={16} className="text-gray-600 mb-1" />
                          <div className={`text-2xl font-bold ${
                            test.metrics.fact_score.after > test.metrics.fact_score.before 
                              ? 'text-green-400' 
                              : test.metrics.fact_score.after < test.metrics.fact_score.before 
                              ? 'text-red-400' 
                              : 'text-gray-400'
                          }`}>
                            {test.metrics.fact_score.after}
                          </div>
                        </div>
                        <div className={`text-xs mt-1 ${
                          test.metrics.fact_score.after > test.metrics.fact_score.before 
                            ? 'text-green-400' 
                            : 'text-red-400'
                        }`}>
                          {test.metrics.fact_score.after > test.metrics.fact_score.before ? '+' : ''}
                          {test.metrics.fact_score.after - test.metrics.fact_score.before}
                        </div>
                      </div>

                      <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50">
                        <div className="text-sm text-gray-400 mb-2">Engagement</div>
                        <div className="flex items-end gap-2">
                          <div className="text-2xl font-bold text-gray-500">{test.metrics.engagement.before}%</div>
                          <ArrowRight size={16} className="text-gray-600 mb-1" />
                          <div className={`text-2xl font-bold ${
                            test.metrics.engagement.after > test.metrics.engagement.before 
                              ? 'text-green-400' 
                              : test.metrics.engagement.after < test.metrics.engagement.before 
                              ? 'text-red-400' 
                              : 'text-gray-400'
                          }`}>
                            {test.metrics.engagement.after}%
                          </div>
                        </div>
                        <div className={`text-xs mt-1 ${
                          test.metrics.engagement.after > test.metrics.engagement.before 
                            ? 'text-green-400' 
                            : 'text-red-400'
                        }`}>
                          {test.metrics.engagement.after > test.metrics.engagement.before ? '+' : ''}
                          {(test.metrics.engagement.after - test.metrics.engagement.before).toFixed(1)}%
                        </div>
                      </div>

                      <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50">
                        <div className="text-sm text-gray-400 mb-2">Скорость (сек)</div>
                        <div className="flex items-end gap-2">
                          <div className="text-2xl font-bold text-gray-500">{test.metrics.speed.before}s</div>
                          <ArrowRight size={16} className="text-gray-600 mb-1" />
                          <div className={`text-2xl font-bold ${
                            test.metrics.speed.after < test.metrics.speed.before 
                              ? 'text-green-400' 
                              : test.metrics.speed.after > test.metrics.speed.before 
                              ? 'text-red-400' 
                              : 'text-gray-400'
                          }`}>
                            {test.metrics.speed.after}s
                          </div>
                        </div>
                        <div className={`text-xs mt-1 ${
                          test.metrics.speed.after < test.metrics.speed.before 
                            ? 'text-green-400' 
                            : 'text-red-400'
                        }`}>
                          {test.metrics.speed.after < test.metrics.speed.before ? '-' : '+'}
                          {Math.abs(test.metrics.speed.after - test.metrics.speed.before)}s
                        </div>
                      </div>
                    </div>

                    {/* Radar Chart */}
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart data={[
                          { metric: 'Quality', before: test.metrics.quality_score.before, after: test.metrics.quality_score.after },
                          { metric: 'Fact Check', before: test.metrics.fact_score.before, after: test.metrics.fact_score.after },
                          { metric: 'Engagement', before: test.metrics.engagement.before * 10, after: test.metrics.engagement.after * 10 },
                          { metric: 'Speed', before: 100 - test.metrics.speed.before, after: 100 - test.metrics.speed.after },
                        ]}>
                          <PolarGrid stroke="#374151" />
                          <PolarAngleAxis dataKey="metric" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                          <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 10 }} />
                          <Radar name="Production" dataKey="before" stroke="#6b7280" fill="#6b7280" fillOpacity={0.3} />
                          <Radar name="Sandbox" dataKey="after" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
                          <Legend />
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                          />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <FlaskConical size={24} className="mr-2" />
              Новый sandbox тест
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">Название теста</label>
                <input
                  type="text"
                  value={newTest.name}
                  onChange={(e) => setNewTest({...newTest, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  placeholder="Prompt v9 vs Production"
                />
              </div>
              
              <div>
                <label className="block text-gray-400 text-sm mb-2">Тип теста</label>
                <select
                  value={newTest.type}
                  onChange={(e) => setNewTest({...newTest, type: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="prompt">Промпт</option>
                  <option value="model">Модель</option>
                  <option value="image">Изображение</option>
                  <option value="workflow">Workflow</option>
                </select>
              </div>
              
              <div>
                <label className="block text-gray-400 text-sm mb-2">Описание</label>
                <textarea
                  value={newTest.description}
                  onChange={(e) => setNewTest({...newTest, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  rows={3}
                  placeholder="Описание изменений..."
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCreateTest}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Запустить тест
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

export default Sandbox;
