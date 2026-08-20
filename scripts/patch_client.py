import pathlib

p = pathlib.Path("/app/frontend/src/api/client.ts")
c = p.read_text(encoding="utf-8")

if "getTemplates" in c:
    print("[i] channelsAPI.getTemplates already exists")
else:
    # Добавляем methods в channelsAPI
    old = '''  get: (id: string) => apiClient.get(`/channels/${id}`),'''
    new = '''  get: (id: string) => apiClient.get(`/channels/${id}`),
  getTemplates: () => apiClient.get('/channels/templates'),
  createFromTemplate: (templateId: string, customName?: string) => 
    apiClient.post('/channels/from-template', null, { params: { template_id: templateId, custom_name: customName } }),'''
    
    if old in c:
        c = c.replace(old, new, 1)
        p.write_text(c, encoding="utf-8")
        print("[OK] Added getTemplates + createFromTemplate to channelsAPI")
    else:
        print("[?] Pattern not found")