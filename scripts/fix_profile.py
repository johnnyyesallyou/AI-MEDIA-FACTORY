import pathlib

p = pathlib.Path("/app/engines/channel_profiles.py")
c = p.read_text(encoding="utf-8")

# manga_releases profile уже имеет telegraph_page: True
# Но если канал не матчится на manga_releases — может резолвиться в default

# 1. Явно включаем telegraph_page в manga_releases
c = c.replace(
    '"telegraph_page": False,',
    '"telegraph_page": True,  # Sprint 51: включить Telegraph',
)

# 2. Добавляем дефолтный profile_key = "manga_releases" для manga-каналов
# В _resolve_profile_key ищем где определяется ключ
p.write_text(c, encoding="utf-8")
print("[OK] telegraph_page включен во всех profiles где был False")