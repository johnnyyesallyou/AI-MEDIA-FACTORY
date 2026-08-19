import pathlib, re
p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8')

# Ищем блок в ResearchJob.run() где есть fallback на hardcoded sources
# Типичный паттерн: "if not sources: sources = [...]"
old_pattern = r'''(class ResearchJob:.*?def run\(.*?\):.*?)if not (channel\.sources|sources):.*?sources\s*=\s*\[(.*?)\]'''

def remove_fallback(match):
    before = match.group(1)
    sources_list = match.group(3)
    # Проверяем содержит ли fallback habr.com или vc.ru
    if 'habr.com' in sources_list or 'vc.ru' in sources_list:
        print(f"   ❌ Найден hardcoded fallback на Habr/VC — удаляем")
        # Заменяем на пустой список + лог + return
        return f'''{before}if not channel.sources or len(channel.sources) == 0:
            logger.warning("Channel has no sources configured, skipping research")
            return {{"status": "skipped", "reason": "No sources configured"}}
        sources = channel.sources'''
    else:
        print(f"   ℹ️ Fallback найден, но не на Habr/VC — оставляем")
        return match.group(0)

s_new, count = re.subn(old_pattern, remove_fallback, s, count=1, flags=re.DOTALL)

if count > 0:
    p.write_text(s_new, encoding='utf-8')
    print(f"✅ Убран hardcoded fallback")
else:
    # Альтернативный паттерн: "if len(sources) == 0"
    old_pattern2 = r'''(class ResearchJob:.*?def run\(.*?\):.*?)if len\(.*?sources.*?\)\s*==\s*0:.*?sources\s*=\s*\[(.*?)\]'''
    s_new, count = re.subn(old_pattern2, remove_fallback, s, count=1, flags=re.DOTALL)
    if count > 0:
        p.write_text(s_new, encoding='utf-8')
        print(f"✅ Убран hardcoded fallback (альтернативный паттерн)")
    else:
        print("⚠️ Паттерн не найден — нужен ручной аудит")
        print("\n   Показываю блок ResearchJob:")
        # Находим начало класса
        lines = s.split('\n')
        in_class = False
        class_lines = []
        for i, line in enumerate(lines):
            if 'class ResearchJob' in line:
                in_class = True
            if in_class:
                class_lines.append(f"{i+1:4d}: {line}")
                if line.strip().startswith('class ') and 'ResearchJob' not in line:
                    break
                if len(class_lines) > 100:
                    break
        print('\n'.join(class_lines[:80]))