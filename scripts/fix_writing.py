import pathlib, re

p = pathlib.Path("/app/backend/automation/jobs/automation_jobs.py")
c = p.read_text(encoding="utf-8")

# В WritingJob: если все items упали — возвращаем failed
# Ищем блок где пишется Writing failed и считаем
old_pattern = '''                except Exception as e:
                    logger.exception("Writing failed item=%s error=%s", item.id, e)
                    db.rollback()'''

new_pattern = '''                except Exception as e:
                    logger.exception("Writing failed item=%s error=%s", item.id, e)
                    db.rollback()
                    failed += 1'''

if old_pattern in c and "failed += 1" not in c[c.index(old_pattern):c.index(old_pattern)+500]:
    c = c.replace(old_pattern, new_pattern, 1)
    
    # И в конце return status
    c = c.replace(
        'return {"status": "ok", "written": written}',
        'return {"status": "ok" if failed == 0 else "partial" if written > 0 else "failed", "written": written, "failed": failed}',
        1,
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] WritingJob возвращает failed/partial при ошибках")
else:
    print("[i] уже исправлено или паттерн не найден")