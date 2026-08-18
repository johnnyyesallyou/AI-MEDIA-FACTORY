import pathlib

p = pathlib.Path("/app/engines/publishing/image_resolver.py")
c = p.read_text(encoding="utf-8")

# 1. Импорт policy
if "ImageAcquisitionPolicy" not in c:
    c = c.replace(
        "from engines.source_image_resolver import SourceImageResolver",
        "from engines.source_image_resolver import SourceImageResolver\nfrom .image_acquisition import ImageAcquisitionPolicy",
        1,
    )

# 2. Init policy в __init__
if "self.acquisition" not in c:
    c = c.replace(
        "self.source_resolver = SourceImageResolver()",
        "self.source_resolver = SourceImageResolver()\n        self.acquisition = ImageAcquisitionPolicy()",
        1,
    )

# 3. AI fallback в resolve() после перебора кандидатов
old = '''        for url in candidates:
            if self.is_valid_image_url(url):
                return url
            elif url:
                self.logger.debug(f"Invalid image candidate: {url[:60]}")

        return None'''

new = '''        real_url = None
        for url in candidates:
            if self.is_valid_image_url(url):
                real_url = url
                break
            elif url:
                self.logger.debug(f"Invalid image candidate: {url[:60]}")

        # Policy-driven acquisition (AI fallback только для news если разрешено)
        result = self.acquisition.acquire(
            content=content,
            real_url=real_url,
            profile=profile,
        )
        return result.url'''

if old in c:
    c = c.replace(old, new, 1)
    print("✅ resolve() uses ImageAcquisitionPolicy")
else:
    print("❌ Marker not found")

p.write_text(c, encoding="utf-8")