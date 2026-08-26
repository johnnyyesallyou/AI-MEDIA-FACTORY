import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

# Добавляем метод _fetch_preview_pages после __init__
preview_method = '''
    def _fetch_preview_pages(self, chapter_url: str, limit: int = 5) -> List[str]:
        """Получает первые N страниц главы с сайта (ReManga/MangaDex)."""
        import requests
        from bs4 import BeautifulSoup
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(chapter_url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return []
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # ReManga: ищем img.reader-page
            if "remanga" in chapter_url:
                imgs = soup.find_all("img", class_="reader-page")
                return [img["src"] for img in imgs[:limit] if img.get("src")]
            
            # MangaDex: ищем img[data-src] в reader
            elif "mangadex" in chapter_url:
                imgs = soup.find_all("img", {"data-src": True})
                return [img["data-src"] for img in imgs[:limit] if img.get("data-src")]
            
            return []
        except Exception as e:
            self.logger.warning(f"Failed to fetch preview pages from {chapter_url}: {e}")
            return []

'''

if "_fetch_preview_pages" not in c:
    c = c.replace(
        '    def __init__(self):',
        '    def __init__(self):' + preview_method,
    )
    print("[OK] Added _fetch_preview_pages method")
else:
    print("[i] _fetch_preview_pages already exists")

p.write_text(c, encoding="utf-8")