import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Workflow } from 'lucide-react';
import axios from 'axios';
import WorkflowDesigner from '../components/workflow/WorkflowDesigner';
import type { BackendWorkflow } from '../types/workflow';

// Если открыты через nginx (:80) — относительный путь, если напрямую (:3001) — абсолютный
const API_BASE =
  window.location.port === '3001' ? 'http://localhost:8000/api/v1' : '/api/v1';

export default function Workflows() {
  const [workflows, setWorkflows] = useState<BackendWorkflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingWorkflow, setEditingWorkflow] = useState<BackendWorkflow | null>(null);
  const [isDesignerOpen, setIsDesignerOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadWorkflows = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/workflows/`);
      setWorkflows(response.data.items || []);
      setError(null);
    } catch (err: any) {
      setError(`Ошибка загрузки: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkflows();
  }, []);

  const handleNew = () => {
    setEditingWorkflow(null);
    setIsDesignerOpen(true);
  };

  const handleEdit = (wf: BackendWorkflow) => {
    setEditingWorkflow(wf);
    setIsDesignerOpen(true);
  };

  const handleSave = async (data: { name: string; description: string; definition: any }) => {
    try {
      setIsSaving(true);
      if (editingWorkflow?.id) {
        await axios.put(`${API_BASE}/workflows/${editingWorkflow.id}`, {
          name: data.name,
          description: data.description,
          definition: data.definition,
          is_active: true,
        });
      } else {
        await axios.post(`${API_BASE}/workflows/`, {
          name: data.name,
          description: data.description,
          definition: data.definition,
          is_active: true,
        });
      }
      setIsDesignerOpen(false);
      setEditingWorkflow(null);
      await loadWorkflows();
    } catch (err: any) {
      alert(`Ошибка сохранения: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (wf: BackendWorkflow) => {
    if (!confirm(`Удалить workflow "${wf.name}"?`)) return;
    try {
      await axios.delete(`${API_BASE}/workflows/${wf.id}`);
      await loadWorkflows();
    } catch (err: any) {
      alert(`Ошибка удаления: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleRun = () => {
    alert('Запуск workflow из дизайнера будет доступен в Sprint 8.5');
  };

  if (isDesignerOpen) {
    return (
      <div className="flex flex-col h-screen bg-gray-900">
        <div className="h-14 bg-gray-800 border-b border-gray-700 px-4 flex items-center gap-3">
          <button
            onClick={() => { setIsDesignerOpen(false); setEditingWorkflow(null); }}
            className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
          >
            ← Назад к списку
          </button>
          <div className="h-6 w-px bg-gray-700" />
          <span className="text-gray-300">
            {editingWorkflow ? `Редактирование: ${editingWorkflow.name}` : 'Новый Workflow'}
          </span>
        </div>
        <div className="flex-1">
          <WorkflowDesigner
            initialWorkflow={editingWorkflow ?? undefined}
            onSave={handleSave}
            onRun={handleRun}
            isSaving={isSaving}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 min-h-screen text-white">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Workflow className="w-7 h-7 text-blue-400" /> Workflows
          </h1>
          <p className="text-gray-400 text-sm mt-1">Визуальный конструктор пайплайнов обработки контента</p>
        </div>
        <button onClick={handleNew} className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" /> Новый Workflow
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">{error}</div>
      )}

      {loading ? (
        <div className="text-center py-20 text-gray-500">Загрузка...</div>
      ) : workflows.length === 0 ? (
        <div className="text-center py-20">
          <Workflow className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-400 mb-2">Нет workflows</h3>
          <button onClick={handleNew} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium">
            Создать Workflow
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workflows.map((wf) => (
            <div key={wf.id} className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-white truncate">{wf.name}</h3>
                  <p className="text-xs text-gray-500 font-mono mt-0.5">{wf.id}</p>
                </div>
                <span className={`px-2 py-0.5 rounded text-xs ${wf.is_active ? 'bg-green-900/50 text-green-400 border border-green-700' : 'bg-gray-700 text-gray-400 border border-gray-600'}`}>
                  {wf.is_active ? 'активен' : 'выключен'}
                </span>
              </div>
              {wf.description && <p className="text-sm text-gray-400 mb-3 line-clamp-2">{wf.description}</p>}
              <div className="flex items-center gap-2 text-xs text-gray-500 mb-4">
                <span>🟦 {wf.definition?.nodes?.length || 0} нод</span>
                <span>•</span>
                <span>🔗 {wf.definition?.edges?.length || 0} связей</span>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => handleEdit(wf)} className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors">
                  <Pencil className="w-3.5 h-3.5" /> Редактировать
                </button>
                <button onClick={() => handleDelete(wf)} className="p-1.5 bg-gray-700 hover:bg-red-600/20 text-red-400 rounded transition-colors" title="Удалить">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}