import pathlib

p = pathlib.Path("/app/main.py")
c = p.read_text(encoding="utf-8")

if "start_alerts_loop" not in c:
    c = c.replace(
        "from backend.automation.scheduler import automation_scheduler",
        "from backend.automation.scheduler import automation_scheduler\nfrom core.alerts import start_alerts_loop",
        1,
    )
    c = c.replace(
        '    asyncio.create_task(automation_scheduler.start())',
        '    asyncio.create_task(automation_scheduler.start())\n\n    # Sprint 44: alerts loop\n    asyncio.create_task(start_alerts_loop())',
        1,
    )
    p.write_text(c, encoding="utf-8")
    print("[OK] alerts loop wired into lifespan")
else:
    print("[i] already wired")