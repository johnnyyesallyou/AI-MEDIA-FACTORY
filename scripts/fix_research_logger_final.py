import pathlib, re

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')

# Патч 1: вставить p_logger.finish перед return {"status": "ok"} в try-блоке
old_try_return = '''                created += 1

            return {
                "status": "ok",
                "topics_received": len(topics),
                "created": created,
                "skipped": skipped
            }'''

new_try_return = '''                created += 1

            p_logger.finish("success", details=f"Created {created}, skipped {skipped}")
            return {
                "status": "ok",
                "topics_received": len(topics),
                "created": created,
                "skipped": skipped
            }'''

if old_try_return in s:
    s = s.replace(old_try_return, new_try_return)
    print('OK: p_logger.finish added before success return')
else:
    print('WARN: try return pattern not found')

# Патч 2: в except-блоке заменить p_logger.finish("success", ...) на p_logger.finish("failed", ...)
old_except_logger = '''        except Exception as e:

            logger.exception(
                "ResearchJob failed"
            )

            p_logger.finish("success", details=f"Created {created}, skipped {skipped}")'''

new_except_logger = '''        except Exception as e:

            error_msg = str(e)
            logger.exception(
                "ResearchJob failed: %s", error_msg
            )

            p_logger.finish("failed", error_message=error_msg)'''

if old_except_logger in s:
    s = s.replace(old_except_logger, new_except_logger)
    print('OK: except block fixed (failed status + error_message)')
else:
    print('WARN: except pattern not found')

# Патч 3: удаляем лишний p_logger.finish перед вторым return (который остался от старого кода)
old_extra_finish = '''            p_logger.finish("success", details=f"Created {created}, skipped {skipped}")


            return {
                "status": "failed",
                "error": str(e)
            }'''

new_extra_finish = '''            return {
                "status": "failed",
                "error": str(e)
            }'''

if old_extra_finish in s:
    s = s.replace(old_extra_finish, new_extra_finish)
    print('OK: extra p_logger.finish removed from except block')

p.write_text(s, encoding='utf-8')
print('DONE')