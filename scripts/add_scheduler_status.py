import pathlib
p = pathlib.Path('./backend/app/api/v1/automation.py')
s = p.read_text(encoding='utf-8')

if 'SchedulerStatusResponse' not in s:
    # Добавляем импорт
    s = s.replace(
        'from backend.automation.manager import automation_manager',
        'from backend.automation.manager import automation_manager\nfrom backend.automation.scheduler import automation_scheduler'
    )
    
    # Добавляем эндпоинт в конец файла
    s += '''

# === SCHEDULER STATUS ===

@router.get("/scheduler/status")
async def get_scheduler_status():
    """Возвращает статус планировщика: запущен ли, сколько задач, следующая задача."""
    if not automation_scheduler.scheduler:
        return {
            "running": False,
            "total_jobs": 0,
            "jobs": []
        }
    
    jobs = automation_scheduler.scheduler.get_jobs()
    jobs_info = []
    for job in jobs:
        channel_id = job.id.replace("channel_", "")
        jobs_info.append({
            "channel_id": channel_id,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "name": job.name
        })
    
    # Сортируем по next_run_time (ближайшие первыми)
    jobs_info.sort(key=lambda x: x["next_run_time"] or "9999")
    
    return {
        "running": automation_scheduler.scheduler.running,
        "total_jobs": len(jobs),
        "jobs": jobs_info
    }
'''
    p.write_text(s, encoding='utf-8')
    print('✅ Добавлен эндпоинт GET /scheduler/status')