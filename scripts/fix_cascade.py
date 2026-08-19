import pathlib

p = pathlib.Path("/app/core/repositories/channel_repository.py")
c = p.read_text(encoding="utf-8")

# 1. Удаляем битый module-level блок (от маркера/def до конца файла)
idx = c.find("def delete_cascade")
if idx != -1:
    cut = c.rfind("# ===", 0, idx)
    if cut == -1:
        cut = idx
    c = c[:cut].rstrip() + "\n"
    print("[1] removed broken module-level block")

# 2. Добавляем ПРАВИЛЬНЫЙ метод класса (с отступом 4)
method = '''
    def delete_cascade(self, channel_id: str) -> bool:
        """Schema-driven cascade delete: удаляет строки из ВСЕХ таблиц,
        имеющих FK на channels, затем сам канал."""
        from sqlalchemy import text
        try:
            channel = self.db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
            if not channel:
                return False

            if self.db.get_bind().dialect.name == "postgresql":
                rows = self.db.execute(text("""
                    SELECT DISTINCT child.relname AS tbl, a.attname AS col
                    FROM pg_constraint c
                    JOIN pg_class parent ON parent.oid = c.confrelid
                    JOIN pg_class child ON child.oid = c.conrelid
                    JOIN unnest(c.conkey) WITH ORDINALITY AS k(attnum, ord) ON TRUE
                    JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum
                    WHERE parent.relname = 'channels' AND c.contype = 'f'
                """)).fetchall()
                for tbl, col in rows:
                    self.db.execute(
                        text('DELETE FROM "' + tbl + '" WHERE "' + col + '" = :cid'),
                        {"cid": channel_id},
                    )
            else:
                from core.models.channel_schedule_orm import ChannelScheduleORM
                self.db.query(ChannelScheduleORM).filter(
                    ChannelScheduleORM.channel_id == channel_id
                ).delete()

            self.db.delete(channel)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            import traceback
            traceback.print_exc()
            return False
'''

c += method
p.write_text(c, encoding="utf-8")
print("[2] delete_cascade added as proper class method")