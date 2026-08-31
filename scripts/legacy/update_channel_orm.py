import pathlib

f = pathlib.Path('./core/models/channel_orm.py')
s = f.read_text(encoding='utf-8')

# Проверяем есть ли уже поля
if 'vk_group_id' in s:
    print("ℹ️ VK поля уже есть в ChannelORM")
else:
    # Вставляем после chat_id
    new_columns = '''
    # Sprint 11: VK credentials
    vk_group_id = Column(String(50), nullable=True)
    vk_access_token = Column(String(255), nullable=True)

    # Sprint 11: YouTube credentials
    youtube_channel_id = Column(String(100), nullable=True)
    youtube_api_key = Column(String(255), nullable=True)
    youtube_access_token = Column(String, nullable=True)
    youtube_refresh_token = Column(String, nullable=True)

    # Sprint 11: Dzen credentials
    dzen_channel_id = Column(String(100), nullable=True)
    dzen_api_key = Column(String(255), nullable=True)
'''
    s = s.replace(
        'chat_id = Column(String, nullable=True)',
        'chat_id = Column(String, nullable=True)' + new_columns,
        1
    )
    f.write_text(s, encoding='utf-8')
    print("✅ Добавлены поля vk_*, youtube_*, dzen_* в ChannelORM")

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ channel_orm.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")