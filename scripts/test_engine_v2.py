import asyncio
from engines.writing.engine import WritingEngine
from engines.writing.models import ContentBrief

async def test():
    brief = ContentBrief(
        topic="Google представила квантовый чип Willow",
        audience="AI-разработчики",
        goal="Рассказать о прорыве в квантовых вычислениях",
        tone="Экспертный",
        length_chars=900,
        call_to_action="Что думаете?",
        key_facts=["Google представила Willow", "Решает задачи за минуты", "Обычному компьютеру нужны миллионы лет"],
        platform="telegram"
    )
    
    engine = WritingEngine()
    result = await engine.generate(brief)
    
    print(f"✅ Generation successful!")
    print(f"Model used: {result['model_used']}")
    print(f"Text length: {len(result['generated_text'])} chars")
    print(f"Validation summary: {result['validation_summary']}")
    print(f"Fact check passed: {result['draft'].fact_check_passed}")
    print(f"Validation issues: {len(result['draft'].validation_issues)}")
    if result['draft'].validation_issues:
        for issue in result['draft'].validation_issues[:3]:
            print(f"  [{issue.severity}] {issue.category}: {issue.message}")

asyncio.run(test())