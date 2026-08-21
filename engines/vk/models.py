from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class VKPublishResult:
    status: str
    post_id: Optional[str]
    published_at: datetime
    text_length: int