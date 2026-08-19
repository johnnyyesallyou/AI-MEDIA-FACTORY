import sys
sys.path.insert(0, '/app')
from engines.image_prompt.engine import ImagePromptEngine

engine = ImagePromptEngine()

print('Тестируем генерацию промпта...')
result = engine.generate_prompt(
    headline='«Магическая битва»: анонсирован 3 сезон',
    text='Студия MAPPA официально подтвердила работу над третьим сезоном. Премьера запланирована на 2027 год.',
    platform='telegram',
    language='en',
    style='anime'
)

print(f'\\n✅ Промпт сгенерирован!')
print(f'   prompt: {result["prompt"]}')
print(f'   negative: {result["negative_prompt"]}')
print(f'   style: {result["style"]}')