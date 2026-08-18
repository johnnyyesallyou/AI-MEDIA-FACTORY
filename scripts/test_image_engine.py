import sys
sys.path.insert(0, '/app')
from engines.image.engine import ImageEngine

engine = ImageEngine()
print('Тестируем генерацию картинки...')

# Тест 1: Аниме постер
result = engine.generate_anime_poster(
    anime_title='Attack on Titan',
    context='final season, epic battle scene'
)

if 'error' in result:
    print(f'❌ Ошибка: {result["error"]}')
else:
    print(f'✅ Картинка сгенерирована!')
    print(f'   URL: {result["image_url"][:100]}...')
    print(f'   Prompt: {result["prompt"][:80]}...')
    print(f'   Model: {result["model"]}')
    
    # Проверяем доступность URL
    import requests
    try:
        r = requests.get(result['image_url'], timeout=10)
        print(f'   HTTP Status: {r.status_code}')
        print(f'   Content-Type: {r.headers.get("content-type", "unknown")}')
        print(f'   Content-Length: {r.headers.get("content-length", "unknown")} bytes')
    except Exception as e:
        print(f'   ⚠️ Не удалось загрузить: {e}')