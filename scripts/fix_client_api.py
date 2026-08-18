import pathlib

client_file = pathlib.Path('./frontend/src/api/client.ts')
s = client_file.read_text(encoding='utf-8')
changes = []

# Добавляем workflowsAPI (если нет)
if 'export const workflowsAPI' not in s:
    workflows_api = '''

// Workflows API
export const workflowsAPI = {
  list: () => apiClient.get('/workflows/'),
  get: (id: string) => apiClient.get(`/workflows/${id}`),
  create: (data: any) => apiClient.post('/workflows/', data),
  update: (id: string, data: any) => apiClient.put(`/workflows/${id}`, data),
  delete: (id: string) => apiClient.delete(`/workflows/${id}`),
};
'''
    # Вставляем перед export const automationAPI
    s = s.replace('export const automationAPI = {', workflows_api + '\nexport const automationAPI = {', 1)
    changes.append("добавлен workflowsAPI")

# Добавляем update метод в channelsAPI (если нет)
if 'update: (id: string, data: any)' not in s:
    update_method = '''    update: (id: string, data: any) => apiClient.put(`/channels/${id}`, data),'''
    # Вставляем после create
    s = s.replace(
        'create: (data: any) => apiClient.post(\'/channels/\', data),',
        'create: (data: any) => apiClient.post(\'/channels/\', data),\n' + update_method,
        1
    )
    changes.append("добавлен channelsAPI.update")

client_file.write_text(s, encoding='utf-8')

if changes:
    print(f"✅ Применено {len(changes)} изменений:")
    for c in changes:
        print(f"   - {c}")
else:
    print("ℹ️ Все методы уже существуют")