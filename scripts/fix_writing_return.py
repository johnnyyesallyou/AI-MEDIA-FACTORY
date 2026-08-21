import pathlib, re

p = pathlib.Path("/app/backend/automation/jobs/automation_jobs.py")
c = p.read_text(encoding="utf-8")

# Ищем финальный return в WritingJob
# Паттерн: return {"status": "ok", "processed": processed}
# или: return {"status": "ok", "items_processed": processed}

old_patterns = [
    'return {"status": "ok", "processed": processed}',
    'return {"status": "ok", "items_processed": processed}',
    'return {"status": "ok", "processed": processed, "failed": failed}',
]

new_pattern = 'return {"status": "ok" if failed == 0 else "partial" if processed > 0 else "failed", "processed": processed, "failed": failed}'

changed = False
for old in old_patterns:
    if old in c:
        c = c.replace(old, new_pattern, 1)
        print(f"[OK] replaced: {old}")
        changed = True
        break

if not changed:
    # Ищем любой return {"status": "ok" в WritingJob
    import re
    match = re.search(r'class WritingJob:.*?def run\(.*?\).*?(return \{[^}]+\})', c, re.DOTALL)
    if match:
        print(f"Found return: {match.group(1)}")
    else:
        print("[!] Could not find WritingJob return statement")

if changed:
    p.write_text(c, encoding="utf-8")
    print("[OK] WritingJob return fixed")
else:
    print("[i] no changes made")