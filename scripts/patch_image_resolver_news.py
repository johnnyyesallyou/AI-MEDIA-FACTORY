import pathlib

p = pathlib.Path("/app/engines/publishing/image_resolver.py")
c = p.read_text(encoding="utf-8")

# 1. Добавляем news в resolve()
old = '''        elif content_type == "anime_release":
            candidates = self._anime_candidates(content)
        else:
            candidates = self._news_candidates(content, image_policy)'''

new = '''        elif content_type == "anime_release":
            candidates = self._anime_candidates(content)
        elif content_type == "news":
            candidates = self._news_candidates(content, image_policy)
        else:
            candidates = self._news_candidates(content, image_policy)'''

if old in c:
    c = c.replace(old, new, 1)
    print("✅ resolve() updated for news")
else:
    print("ℹ️ Already updated or marker not found")

p.write_text(c, encoding="utf-8")