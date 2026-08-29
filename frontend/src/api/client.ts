import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard API
export const dashboardAPI = {
  getHealth: () => apiClient.get('/dashboard/health'),
  getStats: () => apiClient.get('/dashboard/stats'),
};

// Channels API
export const channelsAPI = {
  list: () => apiClient.get('/channels/'),
  get: (id: string) => apiClient.get(`/channels/${id}`),
  getTemplates: () => apiClient.get('/channels/templates'),
  createFromTemplate: (templateId: string) => apiClient.post(`/channels/from-template?template_id=${templateId}`),
  create: (data: any) => apiClient.post('/channels/', data),
  update: (id: string, data: any) => apiClient.put(`/channels/${id}`, data),
  delete: (id: string) => apiClient.delete(`/channels/${id}`),
  connectTelegram: (id: string, data: any) => apiClient.post(`/channels/${id}/connect-telegram`, data),
    connectVk: (id: string, data: any) => apiClient.post(`/channels/${id}/connect-vk`, data),
    connectYoutube: (id: string, data: any) => apiClient.post(`/channels/${id}/connect-youtube`, data),
    connectDzen: (id: string, data: any) => apiClient.post(`/channels/${id}/connect-dzen`, data),
  addSource: (id: string, data: any) => apiClient.post(`/channels/${id}/sources`, data),
  listSources: (id: string) => apiClient.get(`/channels/${id}/sources`),
  deleteSource: (id: string, sourceId: string) => apiClient.delete(`/channels/${id}/sources/${sourceId}`),
  getSchedule: (id: string) => apiClient.get(`/channels/${id}/schedule`),
  updateSchedule: (id: string, data: any) => apiClient.put(`/channels/${id}/schedule`, data),
};

// Content API
export const contentAPI = {
  list: (status?: string) => apiClient.get('/content/', { params: { status } }),
  get: (id: string) => apiClient.get(`/content/${id}`),
  updateStatus: (id: string, status: string) => apiClient.put(`/content/${id}/status`, { status }),
};

// AI Models API
export const aiAPI = {
  listModels: () => apiClient.get('/ai/models'),
  getRouting: () => apiClient.get('/ai/routing'),
  updateRouting: (data: any) => apiClient.put('/ai/routing', data),
};

// Automation API


// Workflows API
export const workflowsAPI = {
  list: () => apiClient.get('/workflows/'),
  get: (id: string) => apiClient.get(`/workflows/${id}`),
  create: (data: any) => apiClient.post('/workflows/', data),
  update: (id: string, data: any) => apiClient.put(`/workflows/${id}`, data),
  delete: (id: string) => apiClient.delete(`/workflows/${id}`),
};

export const automationAPI = {
  getSchedulerStatus: () => apiClient.get('/automation/scheduler/status'),
  get: () => apiClient.get('/automation/'),
  update: (data: any) => apiClient.put('/automation/', data),
  runNow: () => apiClient.post('/automation/run-now'),
  retry: (execution_id: string, stage: string) => apiClient.post('/automation/retry', { execution_id, stage }), // ДОБАВЛЕНО
};


// Mock-данные для AI Models (когда API не реализован)
const mockRoutingConfig = [
  { task_name: 'research', current_model_id: 'gpt-4o', fallback_model_id: 'qwen3-32b', temperature: 0.7, updated_at: new Date().toISOString() },
  { task_name: 'writing', current_model_id: 'qwen3-32b', fallback_model_id: 'gpt-4o', temperature: 0.8, updated_at: new Date().toISOString() },
  { task_name: 'fact_check', current_model_id: 'gpt-4o-mini', fallback_model_id: null, temperature: 0.3, updated_at: new Date().toISOString() },
  { task_name: 'evaluator', current_model_id: 'qwen3-32b', fallback_model_id: 'gpt-4o', temperature: 0.5, updated_at: new Date().toISOString() },
];

const mockModelsList = [
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI', context_window: 128000, is_active: true },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'OpenAI', context_window: 128000, is_active: true },
  { id: 'qwen3-32b', name: 'Qwen3 32B', provider: 'Alibaba', context_window: 32768, is_active: true },
  { id: 'llama-3.1-70b', name: 'Llama 3.1 70B', provider: 'Meta', context_window: 128000, is_active: false },
];

// Analytics API
export const analyticsAPI = {
  getOverview: () => apiClient.get('/analytics/overview'),
  getBestPerformers: () => apiClient.get('/analytics/best-performers'),
  getTimeSeries: (days: number = 7) => apiClient.get('/analytics/time-series', { params: { days } }),
};

// Knowledge API
export const knowledgeAPI = {
  listInsights: (category?: string) => apiClient.get('/knowledge/insights', { params: { category } }),
  createInsight: (data: any) => apiClient.post('/knowledge/insights', data),
  deleteInsight: (id: string) => apiClient.delete(`/knowledge/insights/${id}`),
};

// Assets API
export const assetsAPI = {
  list: (type?: string) => apiClient.get('/assets/', { params: { asset_type: type } }),
  upload: (file: File, type: string) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/assets/upload', formData, {
      params: { asset_type: type },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// Integrations API
export const integrationsAPI = {
  list: () => apiClient.get('/integrations/'),
  check: (id: string) => apiClient.post(`/integrations/${id}/check`),
};


// Metrics API (Sprint 43 — system metrics from Prometheus + health)
export const metricsAPI = {
  getSystem: () => apiClient.get('/metrics/system'),
};

// Logs API
export const logsAPI = {
  list: (limit: number = 50) => apiClient.get('/logs/', { params: { limit } }),
  get: (id: string) => apiClient.get(`/logs/${id}`),
};

// Users API
export const usersAPI = {
  getMe: () => apiClient.get('/users/me'),
  list: () => apiClient.get('/users/'),
  create: (data: any) => apiClient.post('/users/', data),
  updateRole: (id: string, role: string) => apiClient.put(`/users/${id}/role`, { role }),
};

// Settings API
export const settingsAPI = {
  get: () => apiClient.get('/settings/'),
  update: (data: any) => apiClient.put('/settings/', data),
  listEnv: () => apiClient.get('/settings/env'),
  triggerBackup: () => apiClient.post('/settings/backup'),
};


// Wizard API (Sprint 55/61)
export const wizardAPI = {
  suggest: (data: any) => apiClient.post('/wizard/suggest', data),
  validate: (config: any) => apiClient.post('/wizard/validate', config),
  create: (data: any) => apiClient.post('/channels/create-from-wizard', data),
};

// Posts API (Sprint 57-60)
export const postsAPI = {
  generate: (channelId: string, data: any) => apiClient.post(`/posts/generate/${channelId}`, data),
  getHistory: (channelId: string, limit: number = 20) => apiClient.get(`/posts/history/${channelId}`, { params: { limit } }),
  getMetrics: (channelId: string, days: number = 7) => apiClient.get(`/posts/metrics/${channelId}`, { params: { days } }),
  getLearnings: (channelId: string, minScore: number = 0.5) => apiClient.get(`/posts/learnings/${channelId}`, { params: { min_score: minScore } }),
};

// Sources API (Sprint 53)
export const sourcesAPI = {
  list: (contentType?: string) => apiClient.get('/sources/', { params: contentType ? { content_type: contentType } : {} }),
  get: (id: string) => apiClient.get(`/sources/${id}`),
  validate: (data: any) => apiClient.post('/sources/validate', data),
};

// Channel Control API (Sprint 56)
export const channelControlAPI = {
  start: (channelId: string) => apiClient.post(`/channels/${channelId}/start`),
  pause: (channelId: string) => apiClient.post(`/channels/${channelId}/pause`),
  status: (channelId: string) => apiClient.get(`/channels/${channelId}/status`),
};

export default apiClient;


// Безопасные версии AI API (с fallback на mock при 404)
export const aiAPISafe = {
  getRouting: async () => {
    try {
      return await aiAPI.getRouting();
    } catch (e: any) {
      if (e?.response?.status === 404) {
        return { data: mockRoutingConfig, _isMock: true };
      }
      throw e;
    }
  },
  listModels: async () => {
    try {
      return await aiAPI.listModels();
    } catch (e: any) {
      if (e?.response?.status === 404) {
        return { data: mockModelsList, _isMock: true };
      }
      throw e;
    }
  },
  updateRouting: aiAPI.updateRouting,
};
