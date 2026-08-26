import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

# Ищем где вычисляется telegraph_url и добавляем сохранение в item
old_block = '''                telegraph_url = result["url"]
                self.logger.info(f"Telegraph: {telegraph_url}")
            except Exception as e:
                self.logger.warning(f"Telegraph failed: {e}")'''

new_block = '''                telegraph_url = result["url"]
                item.telegraph_url = telegraph_url  # Sprint 51: сохраняем в БД
                self.logger.info(f"Telegraph: {telegraph_url}")
                db.commit()  # Sprint 51: commit чтобы сохранить telegraph_url
            except Exception as e:
                self.logger.warning(f"Telegraph failed: {e}")
                telegraph_url = None'''

if old_block in c and "item.telegraph_url = telegraph_url" not in c:
    c = c.replace(old_block, new_block, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] Добавлено сохранение telegraph_url в ContentORM + commit")
else:
    print("[i] Уже исправлено или паттерн не найден")