import sys
sys.path.insert(0, '/app')
from engines.asset.manager import AssetManager

manager = AssetManager()

print('Тестируем сохранение картинки из Pollinations...')

# Тестовый URL из Pollinations
test_url = 'https://image.pollinations.ai/prompt/jujutsu%20kaisen%20anime%20poster,%20high%20quality?width=1024&height=576&model=flux&nologo=true'

# content_id = наш тестовый пост
content_id = 'd0044fcc-6fc7-4c06-b7d8-1ebca4b39bc0'

asset = manager.save_from_url(
    image_url=test_url,
    content_id=content_id,
    prompt='jujutsu kaisen anime poster, high quality',
    model='pollinations-flux',
    width=1024,
    height=576
)

if asset:
    print(f'\\n✅ Asset сохранён!')
    print(f'   id: {asset.id}')
    print(f'   storage_path: {asset.storage_path}')
    print(f'   public_url: {asset.public_url}')
    print(f'   generation_time_ms: {asset.generation_time_ms}')
else:
    print('❌ Не удалось сохранить asset')