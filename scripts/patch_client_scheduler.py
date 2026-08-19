import pathlib
p = pathlib.Path('./frontend/src/api/client.ts')
c = p.read_text(encoding='utf-8')

if 'getSchedulerStatus' not in c:
    # Добавляем automationAPI перед закрывающей }
    c = c.replace(
        '  updateSchedule: (id: string, data: any) => apiClient.put(`/channels/${id}/schedule`, data),\n};',
        '  updateSchedule: (id: string, data: any) => apiClient.put(`/channels/${id}/schedule`, data),\n};\n\n// Automation API\nexport const automationAPI = {\n  getSchedulerStatus: () => apiClient.get(\'/automation/scheduler/status\'),\n};'
    )
    p.write_text(c, encoding='utf-8')
    print('✅ client.ts: добавлен automationAPI.getSchedulerStatus')