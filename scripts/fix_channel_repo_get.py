import pathlib
p = pathlib.Path('./core/repositories/channel_repository.py')
s = p.read_text(encoding='utf-8')
changes = []

# Ищем метод get() и добавляем безопасную обработку sources
old_get = '''    def get(self, channel_id: str) -> Optional[ChannelORM]:
        """Получить канал по ID."""
        return self.db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()'''

new_get = '''    def get(self, channel_id: str) -> Optional[ChannelORM]:
        """Получить канал по ID."""
        channel = self.db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
        if channel:
            # Безопасная обработка sources (может быть None или не-список)
            if channel.sources is None:
                channel.sources = []
            elif not isinstance(channel.sources, list):
                channel.sources = []
        return channel'''

if old_get in s:
    s = s.replace(old_get, new_get, 1)
    changes.append('added safe sources handling in get()')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы:')
    for c in changes:
        print(f'   ✅ {c}')
else:
    print('ℹ️ Метод уже исправлен или отличается')