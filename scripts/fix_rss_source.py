import pathlib

rss_file = pathlib.Path('./engines/research/sources/rss.py')
s = rss_file.read_text(encoding='utf-8')
changes = []

# Ищем __init__ в RSSSource и адаптируем к формату из БД
# Формат из БД: {id, name, source_type, url, priority, is_active}
# RSSSource может ждать: {url, name, max_items} или похожее

# Добавим безопасное чтение url и name из конфига
old_init = '    def __init__(self, config: dict):'
if old_init in s:
    # Проверяем что внутри __init__
    init_idx = s.find(old_init)
    init_body = s[init_idx:init_idx + 500]
    print(f"Текущий __init__:\n{init_body[:400]}")
    
    # Если есть self.url = config.get('url') или self.url = config['url'], то всё ок
    # Но добавим обработку разных форматов
    if 'self.url = config' not in init_body and "self.url = config['url']" not in init_body:
        print("⚠️ Не нашёл как читается url — показываю весь __init__")

# Универсальный фикс: добавим нормализацию конфига в начале __init__
normalize_block = '''    def __init__(self, config: dict):
        # Нормализация: поддерживаем формат из БД (id, name, url, priority, is_active)
        # и старый формат из config.py
        if isinstance(config, dict):
            # Из БД может прийти is_active=False — пропускаем такие источники
            if not config.get("is_active", True):
                raise ValueError(f"Source {config.get('name', 'unknown')} is inactive")
            
            self.url = config.get("url") or config.get("link") or config.get("feed_url", "")
            self.name = config.get("name") or config.get("title") or "Unknown"
            self.max_items = config.get("max_items", 20)
        else:
            self.url = ""
            self.name = "Unknown"
            self.max_items = 20'''

# Ищем текущий __init__ и заменяем
import re
init_pattern = r'    def __init__\(self, config: dict\):[^\n]*\n(?:[^\n]*\n){0,15}'
match = re.search(init_pattern, s)
if match:
    old_init_body = match.group(0)
    print(f"\n🔄 Заменяем __init__:")
    print(f"   OLD ({len(old_init_body)} chars)")
    print(f"   NEW: нормализация + проверка is_active")
    s = s.replace(old_init_body, normalize_block + '\n', 1)
    changes.append("RSSSource.__init__ адаптирован к формату из БД")

if changes:
    rss_file.write_text(s, encoding='utf-8')
    print(f"\n✅ Применено {len(changes)} фиксов")
else:
    print("\n⚠️ Изменения не применены")