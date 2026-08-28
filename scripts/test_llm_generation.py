import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from engines.content_context import ChannelContext
from engines.prompt_builder import PromptBuilder
from engines.llm_generator import LLMGenerator

db = SessionLocal()
try:
    # 1. Получаем news канал
    channel = db.query(ChannelORM).filter(ChannelORM.id == "24df0f84-46c2-4df4-ab39-d76881b35438").first()
    if not channel:
        print("[!] News channel not found")
        sys.exit(1)
    
    print(f"Channel: {channel.name}")
    
    # 2. Создаём контекст
    context = ChannelContext(channel, db)
    ctx_dict = context.to_prompt_context()
    print(f"\nContext:")
    print(f"  platform: {ctx_dict['platform']}")
    print(f"  theme: {ctx_dict['theme']}")
    print(f"  audience: {ctx_dict['audience']}")
    print(f"  patterns: {ctx_dict['working_patterns']}")
    
    # 3. Строим промпт
    builder = PromptBuilder(context)
    article = {
        "title": "OpenAI представила новую модель GPT-5",
        "source_name": "TechCrunch",
        "summary": "Компания OpenAI анонсировала выпуск GPT-5 с улучшенными возможностями reasoning и мультимодальности."
    }
    prompt = builder.build_news_prompt(article)
    
    print(f"\nPrompt (первые 500 символов):")
    print(prompt[:500])
    print("...")
    
    # 4. Генерируем
    generator = LLMGenerator()
    print("\nGenerating...")
    text = generator.generate(prompt, max_tokens=300)
    
    if text:
        print(f"\n✅ Generated post ({len(text)} chars):")
        print(text)
    else:
        print("\n❌ Generation failed")
        
finally:
    db.close()