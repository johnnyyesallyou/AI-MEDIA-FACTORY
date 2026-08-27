import pathlib

p = pathlib.Path("/app/backend/app/api/v1/channel_control.py")
c = p.read_text(encoding="utf-8")

# Проблема: @router.get("/dashboard") конфликтует с /{channel_id}
# Решение: используем отдельный router с prefix="/dashboard"

old_dashboard = '''@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(db: Session = Depends(get_db)):'''

new_dashboard = '''@router.get("", response_model=DashboardResponse)
async def get_dashboard(db: Session = Depends(get_db)):'''

if old_dashboard in c:
    # Изменяем endpoint path
    c = c.replace(old_dashboard, new_dashboard)
    
    # Изменяем router prefix
    c = c.replace(
        'router = APIRouter(prefix="/channels", tags=["channels"])',
        'router = APIRouter(prefix="/dashboard", tags=["dashboard"])'
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] Dashboard endpoint перемещён на /dashboard")
else:
    print("[!] Pattern not found")