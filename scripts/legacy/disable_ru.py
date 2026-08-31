import pathlib

p = pathlib.Path("/app/engines/channel_profiles.py")
c = p.read_text(encoding="utf-8")

# Временно отключаем RU-фильтр для manga_releases
c = c.replace(
    '''        "publishing_policy": {
            "require_ru_title": True,
            "strip_non_ru_description": True,''',
    '''        "publishing_policy": {
            "require_ru_title": False,  # Sprint 51: временно для теста
            "strip_non_ru_description": False,  # Sprint 51: временно для теста'''
)

p.write_text(c, encoding="utf-8")
print("[OK] RU-фильтр временно отключён для manga_releases")