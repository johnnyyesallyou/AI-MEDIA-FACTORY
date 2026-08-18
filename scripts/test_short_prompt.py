import sys, urllib.parse
sys.path.insert(0, '/app')
from engines.image_prompt.engine import ImagePromptEngine

engine = ImagePromptEngine()

result = engine.generate_prompt(
    headline='«Магическая битва»: анонсирован 3 сезон',
    text='Студия MAPPA анонсировала третий сезон.',
    platform='telegram',
    style='anime'
)

prompt = result['prompt']
print(f'Промпт: {prompt}')
print(f'Длина промпта: {len(prompt)} символов')

# Формируем URL
encoded = urllib.parse.quote(prompt, safe='')
url = f'https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&model=flux&nologo=true'
print(f'\\nURL длина: {len(url)} символов')
print(f'URL: {url[:120]}...')

# Тестируем скачивание
import requests
response = requests.get(url, timeout=60)
print(f'\\nStatus: {response.status_code}')
print(f'Размер: {len(response.content)} bytes')

if len(response.content) > 1000:
    print('✅ КОРОТКИЙ ПРОМПТ РАБОТАЕТ!')
else:
    print('❌ Всё ещё пустой')