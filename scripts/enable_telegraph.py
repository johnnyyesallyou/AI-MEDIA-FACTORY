import pathlib

p = pathlib.Path("/app/engines/channel_profiles.py")
c = p.read_text(encoding="utf-8")

# Ищем manga_releases profile и включаем telegraph_page
if '"telegraph_page": False' in c:
    # Заменяем только в manga_releases profile
    # Ищем блок manga_releases
    start = c.find('"manga_releases":')
    if start != -1:
        # Находим следующий profile или конец
        end = c.find('\n    "', start + 20)
        if end == -1:
            end = c.find('\n}', start)
        
        manga_block = c[start:end]
        manga_block_new = manga_block.replace('"telegraph_page": False', '"telegraph_page": True')
        c = c[:start] + manga_block_new + c[end:]
        p.write_text(c, encoding="utf-8")
        print("[OK] telegraph_page включен в manga_releases profile")
    else:
        print("[!] manga_releases profile not found")
else:
    print("[i] telegraph_page уже True или не найден")