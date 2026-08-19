import sys
sys.path.insert(0, '/app')
from backend.automation.publishers.vk import VkPublisher

pub = VkPublisher()
result = pub.publish(
    text='🤖 Тестовый пост от AI Media Factory (Sprint 11)\n\nПлатформа успешно интегрирована с VK API!\n\n#AI #MediaFactory #тест',
    credentials={
        'group_id': '-240792540',
        'access_token': 'vk1.a.Dj8bVmWpOX8sg7fWjqE587ha1F9gP-FuimHxR8e80g18trZ0_dEJWrHG-11dFk4eGEooviCwBFhjFiHKNUIJr-FRW8VmHd3H2r_HVzjA01WwPVZKM_35RFXMr0UcVOZmkIx5FPs2IKNcUcqZedHnIy1peBXvGqt1BzzYI8PDx2WrjyUURG5puU-oa4xHdygSqkH2Ny-191U1FFG3a19OKA'
    }
)
print(f'success: {result.success}')
print(f'message_id: {result.message_id}')
print(f'error: {result.error}')
if result.platform_data:
    print(f'platform_data: {result.platform_data}')
if result.success:
    print('🎉 ПОСТ ОПУБЛИКОВАН В VK!')