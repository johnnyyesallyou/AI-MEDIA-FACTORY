import pathlib

p = pathlib.Path("/app/main.py")
c = p.read_text(encoding="utf-8")

if "jobs_registry" not in c:
    # Добавляем import после других imports
    c = c.replace(
        "from backend.automation.scheduler import automation_scheduler",
        "from backend.automation.scheduler import automation_scheduler\nfrom backend.automation.runtime.jobs_registry import register_all_jobs",
        1,
    )
    
    # Вызываем register_all_jobs в начале lifespan
    c = c.replace(
        "    print(\"🚀 Backend starting\", flush=True)",
        "    print(\"🚀 Backend starting\", flush=True)\n    register_all_jobs()  # Sprint 48: load all job types",
        1,
    )
    
    p.write_text(c, encoding="utf-8")
    print("[OK] jobs_registry импортирован в main.py")
else:
    print("[i] already imported")