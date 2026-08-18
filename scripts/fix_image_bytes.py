import pathlib

p = pathlib.Path("/app/backend/automation/jobs/news_publish_job.py")
c = p.read_text(encoding="utf-8")

# Добавляем import requests (если ещё нет)
if "import requests" not in c:
    c = c.replace(
        "import html as html_lib",
        "import html as html_lib\nimport requests",
        1,
    )
    print("✅ Added import requests")

# Находим маркер перед использованием image_bytes и вставляем определение
marker = '''        # Сохраняем bytes в metadata для передачи в publisher
        if image_bytes:
            publication.metadata["_image_bytes"] = image_bytes'''

download_block = '''        # Скачиваем картинку (Habr URLs без расширения ломают sendPhoto)
        image_bytes = None
        if image_url:
            try:
                headers = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
                r = requests.get(image_url, headers=headers, timeout=15)
                if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                    image_bytes = r.content
                    self.logger.debug(f"Downloaded image: {len(image_bytes)} bytes from {image_url[:60]}")
                else:
                    self.logger.warning(f"Image download failed: status={r.status_code}, ct={r.headers.get('content-type')}")
            except Exception as e:
                self.logger.warning(f"Image download error: {e}")

        # Сохраняем bytes в metadata для передачи в publisher
        if image_bytes:
            publication.metadata["_image_bytes"] = image_bytes'''

if marker in c and "image_bytes = None" not in c:
    c = c.replace(marker, download_block, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ image_bytes definition added")
elif "image_bytes = None" in c:
    print("ℹ️ image_bytes already defined")
else:
    print("❌ Marker not found")