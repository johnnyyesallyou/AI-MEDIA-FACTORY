import pathlib
import ast

# ??????? ??? ????????? ????? ???????? ??????? ? encoding
content = """import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey

from core.database import Base


class ChannelORM(Base):
    __tablename__ = "channels"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    platform = Column(String, default="telegram")
    language_search = Column(String, default="en")
    language_publish = Column(String, default="ru")
    style_profile = Column(String, default="minimal")
    timezone = Column(String, default="UTC")
    description = Column(String, nullable=True)

    # Sprint 14: Image profile configuration
    image_profile = Column(JSON, nullable=True, default=dict)

    bot_token = Column(String, nullable=True)
    chat_id = Column(String, nullable=True)
    vk_group_id = Column(String(50), nullable=True)
    vk_access_token = Column(String(255), nullable=True)

    youtube_channel_id = Column(String(100), nullable=True)
    youtube_api_key = Column(String(255), nullable=True)
    youtube_access_token = Column(String, nullable=True)
    youtube_refresh_token = Column(String, nullable=True)

    dzen_channel_id = Column(String(100), nullable=True)
    dzen_api_key = Column(String(255), nullable=True)

    is_connected = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    workflow_id = Column(String, nullable=True, index=True)

    template_id = Column(String, ForeignKey("channel_templates.id"), nullable=True, index=True)
    profile_id = Column(String, ForeignKey("channel_profiles.id"), nullable=True, index=True)

    sources = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
"""

# ????????? ????????? ?? ??????
try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    exit(1)

# ?????????? ???? ?????? ?????????? ? ??????????? ???????????
f = pathlib.Path('/app/core/models/channel_orm.py')
f.write_text(content, encoding='utf-8', newline='\n')

# ?????? ??????? ? ?????????
content_read = f.read_text(encoding='utf-8')
print(f"FILE SIZE: {len(content_read)} bytes")
print(f"FIRST LINE: {content_read.split(chr(10))[0]}")

# ???????? ??? ??? BOM
if content_read.startswith('\ufeff'):
    print("ERROR: BOM detected!")
    exit(1)

# ???????? ????????
lines = content_read.split('\n')
for i, line in enumerate(lines, 1):
    if i == 23 and 'description' in line:
        if line.startswith('    description'):
            print(f"LINE 23 OK: '{line}'")
        else:
            print(f"LINE 23 BAD: '{line}'")
            print(f"  repr: {repr(line)}")

print("SUCCESS")
