import pathlib, re
p = pathlib.Path('./core/repositories/channel_repository.py')
s = p.read_text(encoding='utf-8')

if 'def remove_source' in s:
    print('ℹ️ Метод уже есть')
else:
    new_method = '''
    def remove_source(self, channel_id: str, source_id: str) -> Optional[ChannelORM]:
        """Удаляет источник по ID из JSON-массива sources канала."""
        channel = self.get(channel_id)
        if not channel:
            return None
        current = channel.sources or []
        new_sources = [s for s in current if s.get("id") != source_id]
        if len(new_sources) == len(current):
            return channel  # не нашли
        channel.sources = new_sources
        channel.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(channel)
        return channel
'''
    # Вставляем перед последним методом (delete)
    if 'def delete(self, channel_id: str) -> bool:' in s:
        s = s.replace('    def delete(self, channel_id: str) -> bool:', new_method + '\n    def delete(self, channel_id: str) -> bool:')
        p.write_text(s, encoding='utf-8')
        print('✅ Добавлен remove_source()')
    else:
        s += new_method
        p.write_text(s, encoding='utf-8')
        print('✅ Добавлен remove_source() (в конец)')