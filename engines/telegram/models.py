from dataclasses import dataclass
from datetime import datetime


@dataclass
class TelegramPublishResult:
    status: str
    message_id: int
    chat_id: str
    published_at: datetime
    text_length: int