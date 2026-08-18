import pathlib

f = pathlib.Path('./frontend/src/api/client.ts')
s = f.read_text(encoding='utf-8')

# Ищем connectTelegram и добавляем рядом connectVk
if 'connectVk' not in s:
    s = s.replace(
        'connectTelegram: (id: string, data: any) => apiClient.post(`/channels/${id}/connect-telegram`, data),',
        'connectTelegram: (id: string, data: any) => apiClient.post(`/channels/${id}/connect-telegram`, data),\n    connectVk: (id: string, data: any) => apiClient.post(`/channels/${id}/connect-vk`, data),\n    connectYoutube: (id: string, data: any) => apiClient.post(`/channels/${id}/connect-youtube`, data),\n    connectDzen: (id: string, data: any) => apiClient.post(`/channels/${id}/connect-dzen`, data),',
        1
    )
    print("✅ Добавлены методы: connectVk, connectYoutube, connectDzen")
    f.write_text(s, encoding='utf-8')
else:
    print("ℹ️ Методы уже существуют")