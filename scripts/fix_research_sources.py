import pathlib

# 1. Переписываем config.py на русские источники
config = pathlib.Path('./engines/research/config.py')
new_config = '''RSS_SOURCES = [
    {
        "name": "habr_ai_hub",
        "url": "https://habr.com/ru/rss/hub/artificial_intelligence/",
        "trust_score": 90,
        "categories": ["ai", "research", "llm"],
        "language": "ru"
    },
    {
        "name": "habr_news",
        "url": "https://habr.com/ru/rss/news/",
        "trust_score": 85,
        "categories": ["ai", "news", "technology"],
        "language": "ru"
    },
    {
        "name": "vc_ru",
        "url": "https://vc.ru/rss",
        "trust_score": 85,
        "categories": ["ai", "business", "technology"],
        "language": "ru"
    },
]
'''
config.write_text(new_config, encoding='utf-8')
print('OK: config.py rewritten with 3 Russian sources')