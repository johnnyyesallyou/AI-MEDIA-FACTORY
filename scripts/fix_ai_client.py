import pathlib
p = pathlib.Path('./frontend/src/api/client.ts')
c = p.read_text(encoding='utf-8')

if 'mockRoutingConfig' not in c:
    mock_data = '''
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
'''
    c = c.replace('// Analytics API', mock_data + '\n// Analytics API')
    print('OK: mock data added to client.ts')

# Делаем безопасные версии API с fallback на mock
if 'getRoutingSafe' not in c:
    safe_methods = '''
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
'''
    c = c + '\n' + safe_methods
    print('OK: safe AI API added')

p.write_text(c, encoding='utf-8')