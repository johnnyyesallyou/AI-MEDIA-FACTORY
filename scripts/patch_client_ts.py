import pathlib
p = pathlib.Path('./frontend/src/api/client.ts')
s = p.read_text(encoding='utf-8')

if 'deleteSource' not in s:
    old = '  listSources: (id: string) => apiClient.get(`/channels/${id}/sources`),'
    new = '''  listSources: (id: string) => apiClient.get(`/channels/${id}/sources`),
  deleteSource: (id: string, sourceId: string) => apiClient.delete(`/channels/${id}/sources/${sourceId}`),'''
    s = s.replace(old, new, 1)
    p.write_text(s, encoding='utf-8')
    print('✅ Добавлен deleteSource в client.ts')
else:
    print('ℹ️ deleteSource уже есть')