import pathlib
p = pathlib.Path('./backend/app/api/v1/automation.py')
s = p.read_text(encoding='utf-8')
if 'from backend.automation.scheduler import automation_scheduler' not in s:
    if 'router = APIRouter' in s:
        s = s.replace('router = APIRouter', 'from backend.automation.scheduler import automation_scheduler\n\nrouter = APIRouter', 1)
        p.write_text(s, encoding='utf-8')
        print('OK: import automation_scheduler added')
    else:
        print('ERROR: anchor not found')
else:
    print('import already present')