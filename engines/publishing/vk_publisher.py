"""VK platform publisher - Sprint 28.

Реализует контракт BasePublisher: publish(Publication) -> result.
- Загрузка фото через photos.getWallUploadServer / saveWallPhoto
- Пост через wall.post
- Кнопки Telegram -> ссылки в тексте (VK не имеет inline-кнопок)
"""
import logging
import requests
from typing import Any, Dict, List, Optional

from .base_publisher import BasePublisher
from .publication import Publication

logger = logging.getLogger(__name__)

VK_API = "https://api.vk.com/method"
VK_VERSION = "5.131"
UA = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}


class VKPlatformPublisher(BasePublisher):
    platform = "vk"

    def __init__(self, access_token: str, group_id: str):
        self._token = access_token
        self._group_id = str(group_id).lstrip("-")
        self.logger = logging.getLogger(self.__class__.__name__)

    def _call(self, method: str, **params) -> Any:
        params.update({"access_token": self._token, "v": VK_VERSION})
        r = requests.post(f"{VK_API}/{method}", data=params, timeout=20)
        data = r.json()
        if "error" in data:
            err = data["error"]
            raise RuntimeError(f"VK API error {err.get('error_code')}: {err.get('error_msg')}")
        return data.get("response", {})

    def publish(self, publication: Publication) -> Dict[str, Any]:
        # 1. Фото (если есть)
        attachments: List[str] = []
        if publication.image_url:
            try:
                photo = self._upload_photo(publication.image_url)
                if photo:
                    attachments.append(photo)
            except Exception as e:
                self.logger.warning(f"VK photo upload failed: {e}")

        # 2. Текст + ссылки вместо inline-кнопок
        message = publication.text
        links = [b.url for b in publication.buttons if b.url]
        if links:
            message = message + "\n\n" + "\n".join(links)

        params = {
            "owner_id": -int(self._group_id),
            "message": message,
            "from_group": 1,
        }
        if attachments:
            params["attachments"] = ",".join(attachments)

        resp = self._call("wall.post", **params)
        post_id = resp.get("post_id")
        url = f"https://vk.com/wall-{self._group_id}_{post_id}"
        self.logger.info(f"VK post created: {url}")
        return {"status": "success", "post_id": post_id, "url": url}

    def _upload_photo(self, image_url: str) -> Optional[str]:
        """Скачивает изображение и загружает в VK."""
        headers = dict(UA)
        if "mangadex" in image_url:
            headers["Referer"] = "https://mangadex.org/"

        img = requests.get(image_url, headers=headers, timeout=20).content
        if not img:
            return None

        server = self._call("photos.getWallUploadServer", group_id=self._group_id)
        up = requests.post(
            server["upload_url"],
            files={"photo": ("cover.jpg", img, "image/jpeg")},
            timeout=30,
        ).json()

        saved = self._call(
            "photos.saveWallPhoto",
            server=up["server"],
            photo=up["photo"],
            hash=up["hash"],
        )
        p = saved[0]
        return f"photo{p['owner_id']}_{p['id']}"