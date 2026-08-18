import pathlib

p = pathlib.Path("/app/engines/publishing/telegram_publisher_adapter.py")
c = p.read_text(encoding="utf-8")

# Заменяем publish метод чтобы использовать image_bytes из metadata
old = '''    def publish(self, publication: Publication) -> Dict[str, Any]:
        buttons = [{"text": b.text, "url": b.url} for b in publication.buttons] or None

        if publication.image_url:
            return self._inner.publish_photo(
                text=publication.text,
                image_url=publication.image_url,
                inline_buttons=buttons,
            )

        if hasattr(self._inner, "publish_text"):
            return self._inner.publish_text(
                text=publication.text,
                inline_buttons=buttons,
            )

        return {"status": "failed", "error": "No image and no publish_text support"}'''

new = '''    def publish(self, publication: Publication) -> Dict[str, Any]:
        buttons = [{"text": b.text, "url": b.url} for b in publication.buttons] or None

        # Проверяем наличие image_bytes в metadata (для news с проблемными URL)
        image_bytes = publication.metadata.get("_image_bytes")
        
        if publication.image_url:
            # Если есть скачанные bytes, отправляем их напрямую через sendPhoto
            if image_bytes:
                return self._publish_photo_bytes(
                    text=publication.text,
                    image_bytes=image_bytes,
                    inline_buttons=buttons,
                )
            
            # Иначе используем URL (для manga/anime covers с расширением)
            return self._inner.publish_photo(
                text=publication.text,
                image_url=publication.image_url,
                inline_buttons=buttons,
            )

        # Fallback: текстовое сообщение
        return self._inner.publish(
            text=publication.text,
            inline_buttons=buttons,
        )
    
    def _publish_photo_bytes(
        self,
        text: str,
        image_bytes: bytes,
        inline_buttons=None,
    ) -> Dict[str, Any]:
        """Отправляет фото из bytes (для news URL без расширения)."""
        import json
        import os
        from engines.telegram.rate_limiter import TelegramRateLimiter
        
        clean_text = text[:1021] + "..." if len(text) > 1024 else text
        
        payload = {
            "chat_id": self._inner.chat_id,
            "caption": clean_text,
        }
        
        if inline_buttons:
            keyboard = {"inline_keyboard": [[{"text": b["text"], "url": b["url"]}] for b in inline_buttons]}
            payload["reply_markup"] = json.dumps(keyboard, ensure_ascii=False)
        
        files = {"photo": ("cover.jpg", image_bytes, "image/jpeg")}
        
        data = self._inner._send_with_retry("sendPhoto", payload, files=files)
        
        if data and data.get("ok"):
            return {
                "status": "success",
                "message_id": data["result"]["message_id"],
                "chat_id": self._inner.chat_id,
            }
        
        # Fallback на text
        return self._inner.publish(text=text, inline_buttons=inline_buttons)'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ TelegramPlatformPublisher: bytes support added")
else:
    print("❌ Marker not found")