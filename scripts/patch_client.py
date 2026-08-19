import pathlib

# 1. client.ts — добавляем методы schedule в channelsAPI
cp = pathlib.Path('./frontend/src/api/client.ts')
c = cp.read_text(encoding='utf-8')
if 'getSchedule' not in c:
    c = c.replace(
        '  listSources: (id: string) => apiClient.get(`/channels/${id}/sources`),\n};',
        '  listSources: (id: string) => apiClient.get(`/channels/${id}/sources`),\n  getSchedule: (id: string) => apiClient.get(`/channels/${id}/schedule`),\n  updateSchedule: (id: string, data: any) => apiClient.put(`/channels/${id}/schedule`, data),\n};'
    )
    cp.write_text(c, encoding='utf-8')
    print('OK client.ts: schedule methods added')