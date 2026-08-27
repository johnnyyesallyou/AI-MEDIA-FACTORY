import pathlib

p = pathlib.Path("/app/engines/telegraph/publisher.py")
c = p.read_text(encoding="utf-8")

# Добавляем метод upload_images_to_telegraph после __init__
upload_method = '''
    def upload_images_to_telegraph(self, urls: List[str]) -> List[str]:
        """Загружает картинки на Telegraph servers и возвращает telegra.ph URLs."""
        import requests
        uploaded_urls = []
        
        for url in urls:
            try:
                # Скачиваем картинку
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://remanga.org/"
                }
                resp = requests.get(url, headers=headers, timeout=15, stream=True)
                
                if resp.status_code != 200:
                    self.logger.warning(f"Failed to download {url[:80]}: status={resp.status_code}")
                    continue
                
                # Загружаем на Telegraph
                upload_resp = requests.post(
                    "https://telegra.ph/upload",
                    files={"file": ("image.jpg", resp.content, "image/jpeg")},
                    timeout=30,
                )
                
                if upload_resp.status_code == 200:
                    data = upload_resp.json()
                    if isinstance(data, list) and data:
                        telegraph_path = data[0].get("src", "")
                        if telegraph_path:
                            telegraph_url = f"https://telegra.ph{telegraph_path}"
                            uploaded_urls.append(telegraph_url)
                            self.logger.info(f"Uploaded to Telegraph: {telegraph_url}")
                else:
                    self.logger.warning(f"Telegraph upload failed: {upload_resp.status_code}")
                    
            except Exception as e:
                self.logger.warning(f"Image upload failed for {url[:80]}: {e}")
        
        return uploaded_urls

'''

# Ищем где вставить (после __init__)
if "upload_images_to_telegraph" not in c:
    # Вставляем после __init__
    c = c.replace(
        '        self.logger = logging.getLogger(self.__class__.__name__)',
        '        self.logger = logging.getLogger(self.__class__.__name__)\n' + upload_method,
    )
    
    # Обновляем build_manga_page_content чтобы загружать preview pages
    old_preview_block = '''        # Превью первой главы (5 страниц)
        if preview_pages and len(preview_pages) > 0:
            content.append({"tag": "hr"})
            content.append({
                "tag": "h4",
                "children": ["📖 Превью первой главы"]
            })

            for i, page_url in enumerate(preview_pages[:5], 1):
                content.append({
                    "tag": "img",
                    "attrs": {"src": page_url}
                })'''
    
    new_preview_block = '''        # Превью первой главы (5 страниц)
        if preview_pages and len(preview_pages) > 0:
            content.append({"tag": "hr"})
            content.append({
                "tag": "h4",
                "children": ["📖 Превью первой главы"]
            })
            
            # Sprint 51: загружаем preview pages на Telegraph servers
            uploaded_urls = self.upload_images_to_telegraph(preview_pages[:5])
            self.logger.info(f"Uploaded {len(uploaded_urls)}/{len(preview_pages[:5])} preview pages to Telegraph")
            
            for page_url in uploaded_urls:
                content.append({
                    "tag": "img",
                    "attrs": {"src": page_url}
                })'''
    
    c = c.replace(old_preview_block, new_preview_block, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] TelegraphPublisher: добавлен upload_images_to_telegraph + используется в build_manga_page_content")
else:
    print("[i] Уже добавлено")