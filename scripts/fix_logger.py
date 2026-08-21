import pathlib

p = pathlib.Path("/app/backend/automation/jobs/automation_jobs.py")
c = p.read_text(encoding="utf-8")

# Фиксим строку 299: p_logger.finish("success", details=f"Processed {processed}, failed {failed}")
old = '        p_logger.finish("success", details=f"Processed {processed}, failed {failed}")'
new = '        logger_status = "success" if failed == 0 else "partial" if processed > 0 else "failed"\n        p_logger.finish(logger_status, details=f"Processed {processed}, failed {failed}")'

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] PipelineLogger: conditional status")
else:
    print("[!] Pattern not found")