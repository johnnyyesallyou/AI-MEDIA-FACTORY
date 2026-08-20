import pathlib
p = pathlib.Path("/app/backend/app/api/v1/system_metrics.py")
c = p.read_text(encoding="utf-8")

if "/debug/jobs" not in c:
    c += """

@router.get("/debug/jobs")
def debug_jobs():
    from backend.automation.runtime.job_factory import JobFactory
    return {"count": len(JobFactory._registry), "keys": sorted(JobFactory._registry.keys())}
"""
    p.write_text(c, encoding="utf-8")
    print("[OK] debug endpoint added")
else:
    print("[i] already there")