"""Telegraph Publisher - создаёт страницы в Telegraph с внешними изображениями."""
import logging
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


class TelegraphPublisher:
    """
    Создаёт страницы в Telegraph для постов.
    
    Features:
    - Использует внешние URL для изображений (не загружаем в Telegraph)
    - Поддержка полного HTML-like контента (без лимита 1024)
    - Возвращает постоянную ссылку telegra.ph/...
    - Превью первой главы (5 страниц)
    
    Sprint 18: Telegram + Telegraph integration
    """
    
    API_URL = "https://api.telegra.ph"
    UPLOAD_URL = "https://telegra.ph/upload"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Инициализация TelegraphPublisher.
        
        Args:
            access_token: Telegraph API access token (из .env или createAccount)
        """
        self.logger = logging.getLogger(self.__class__.__name__)


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


        self.access_token = access_token or os.getenv("TELEGRAPH_ACCESS_TOKEN")
        
        if not self.access_token:
            self.logger.warning("TELEGRAPH_ACCESS_TOKEN not set, will create new account")
    
    def create_account(self, short_name: str, author_name: str, author_url: str = "") -> str:
        """
        Создаёт новый Telegraph account и возвращает access_token.
        """
        self.logger.info(f"Creating Telegraph account: {short_name}")
        
        response = requests.post(
            f"{self.API_URL}/createAccount",
            data={
                "short_name": short_name,
                "author_name": author_name,
                "author_url": author_url,
            },
            headers=self.HEADERS,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        if not data.get("ok"):
            raise Exception(f"Telegraph createAccount failed: {data}")
        
        self.access_token = data["result"]["access_token"]
        self.logger.info(f"Telegraph account created, token: {self.access_token[:20]}...")
        
        return self.access_token
    
    def create_page(
        self,
        title: str,
        content: List[Dict[str, Any]],
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
        return_content: bool = False
    ) -> Dict[str, Any]:
        """
        Создаёт новую страницу в Telegraph.
        """
        if not self.access_token:
            raise Exception("Access token not set. Call create_account() first.")
        
        self.logger.info(f"Creating Telegraph page: {title[:50]}...")
        
        data = {
            "access_token": self.access_token,
            "title": title[:256],
            "content": json.dumps(content),
            "return_content": "true" if return_content else "false",
        }
        
        if author_name:
            data["author_name"] = author_name[:128]
        if author_url:
            data["author_url"] = author_url[:512]
        
        response = requests.post(
            f"{self.API_URL}/createPage",
            data=data,
            headers=self.HEADERS,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if not result.get("ok"):
            raise Exception(f"Telegraph createPage failed: {result}")
        
        page = result["result"]
        self.logger.info(f"Telegraph page created: {page['url']}")
        
        return {
            "url": page["url"],
            "path": page["path"],
            "title": page["title"],
            "description": page.get("description", ""),
            "author_name": page.get("author_name", ""),
        }
    
    def build_manga_page_content(
        self,
        description: str,
        cover_url: Optional[str],
        source_url: str,
        chapter_url: str,
        preview_pages: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Строит content для манга-страницы с превью первой главы.
        
        Args:
            description: Описание манги
            cover_url: URL обложки (внешний, не загружаем в Telegraph)
            source_url: URL источника (ReManga/MangaDex)
            chapter_url: URL конкретной главы
            preview_pages: Список URL страниц первой главы (5 штук)
        
        Returns:
            List of Telegraph nodes
        """
        content = []
        
        # Обложка (внешний URL)
        if cover_url:
            content.append({
                "tag": "img",
                "attrs": {"src": cover_url}
            })
        
        # Описание
        if description:
            paragraphs = description.split("\n\n")
            for para in paragraphs:
                if para.strip():
                    content.append({
                        "tag": "p",
                        "children": [para.strip()]
                    })
        
        # Превью первой главы (5 страниц)
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
                })
        
        # Разделитель
        content.append({"tag": "hr"})
        
        # Ссылки
        content.append({
            "tag": "h4",
            "children": ["🔗 Ссылки"]
        })
        
        if chapter_url:
            content.append({
                "tag": "p",
                "children": [
                    "📖 ",
                    {"tag": "a", "attrs": {"href": chapter_url}, "children": ["Читать главу"]}
                ]
            })
        
        if source_url:
            content.append({
                "tag": "p",
                "children": [
                    "🌐 ",
                    {"tag": "a", "attrs": {"href": source_url}, "children": ["Страница манги"]}
                ]
            })
        
        # Footer
        content.append({"tag": "hr"})
        content.append({
            "tag": "p",
            "children": [
                {"tag": "i", "children": ["Опубликовано AI Media Factory"]}
            ]
        })
        
        return content
    
    def publish_manga_page(
        self,
        title: str,
        description: str,
        cover_url: Optional[str],
        source_url: str,
        chapter_url: str,
        preview_pages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Создаёт полную Telegraph страницу для манга-поста с превью.
        
        Args:
            title: Заголовок (например "Потомки героя — глава 5")
            description: Описание манги
            cover_url: URL обложки
            source_url: URL источника
            chapter_url: URL главы
            preview_pages: Список URL страниц первой главы (5 штук)
        
        Returns:
            Dict с url, path, title
        """
        content = self.build_manga_page_content(
            description=description,
            cover_url=cover_url,
            source_url=source_url,
            chapter_url=chapter_url,
            preview_pages=preview_pages
        )
        
        return self.create_page(
            title=title,
            content=content,
            author_name="AI Media Factory",
            author_url="https://github.com/yourusername/ai-media-factory"
        )