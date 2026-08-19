import pathlib

p = pathlib.Path("/app/engines/telegram/publisher.py")
c = p.read_text(encoding="utf-8")

# Унифицируем статус: published -> success
old = '''            return {
                "status": "published",
                "message_id": data["result"]["message_id"],
                "chat_id": self.chat_id
            }'''

new = '''            return {
                "status": "success",
                "message_id": data["result"]["message_id"],
                "chat_id": self.chat_id
            }'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ TelegramPublisher: unified status 'success'")
else:
    print("ℹ️ Already fixed or marker not found")