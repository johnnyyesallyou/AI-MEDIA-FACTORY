import pathlib

p = pathlib.Path('./backend/app/api/v1/templates.py')
s = p.read_text(encoding='utf-8')

old_import = '''from backend.app.schemas.templates_schemas import (
    ChannelProfileCreate, ChannelProfileUpdate, ChannelProfileResponse,
    ChannelTemplateCreate, ChannelTemplateUpdate, ChannelTemplateResponse,
    ApplyTemplateRequest, ApplyTemplateResponse
)'''

new_import = '''from .schemas import (
    ChannelProfileCreate, ChannelProfileUpdate, ChannelProfileResponse,
    ChannelTemplateCreate, ChannelTemplateUpdate, ChannelTemplateResponse,
    ApplyTemplateRequest, ApplyTemplateResponse
)'''

if old_import in s:
    s = s.replace(old_import, new_import, 1)
    p.write_text(s, encoding='utf-8')
    print('OK: импорт исправлен на относительный (.schemas)')
else:
    print('ℹ️ импорт уже исправлен или отличается')