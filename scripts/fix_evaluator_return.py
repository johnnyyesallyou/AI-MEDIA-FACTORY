import pathlib

p = pathlib.Path("/app/backend/automation/jobs/automation_jobs.py")
c = p.read_text(encoding="utf-8")

# Ищем EvaluatorJob.run (строки 303-400)
# Паттерн: return {"status": "ok", "approved": approved, "rejected": rejected}
old = '        return {"status": "ok", "approved": approved, "rejected": rejected}'
new = '        status = "ok" if rejected == 0 else "partial" if approved > 0 else "failed"\n        return {"status": status, "approved": approved, "rejected": rejected}'

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] EvaluatorJob return: conditional status")
else:
    print("[!] Pattern not found")