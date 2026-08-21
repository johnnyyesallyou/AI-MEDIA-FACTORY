import pathlib

p = pathlib.Path("/app/backend/automation/jobs/automation_jobs.py")
c = p.read_text(encoding="utf-8")

# Фиксим строку 300: return {"status": "ok", "items_processed": processed, "failed": failed}
old = '        return {"status": "ok", "items_processed": processed, "failed": failed}'
new = '        status = "ok" if failed == 0 else "partial" if processed > 0 else "failed"\n        return {"status": status, "items_processed": processed, "failed": failed}'

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] WritingJob return: conditional status based on failed/processed")
else:
    print("[!] Pattern not found")