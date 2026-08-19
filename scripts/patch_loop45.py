import pathlib

p = pathlib.Path("/app/main.py")
c = p.read_text(encoding="utf-8")

if "start_feedback_loop" not in c:
    c = c.replace(
        "from core.alerts import start_alerts_loop",
        "from core.alerts import start_alerts_loop\nfrom engines.content_optimization.feedback_loop import start_feedback_loop",
        1,
    )
    c = c.replace(
        '    # Sprint 44: alerts loop\n    asyncio.create_task(start_alerts_loop())',
        '    # Sprint 44: alerts loop\n    asyncio.create_task(start_alerts_loop())\n\n    # Sprint 45: feedback loop\n    asyncio.create_task(start_feedback_loop(interval_hours=6))',
        1,
    )
    p.write_text(c, encoding="utf-8")
    print("[OK] feedback loop wired into lifespan")
else:
    print("[i] already wired")