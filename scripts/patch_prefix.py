import pathlib
p = pathlib.Path("/app/backend/app/api/v1/system_metrics.py")
c = p.read_text(encoding="utf-8")
if 'prefix="/api/metrics"' in c:
    c = c.replace('prefix="/api/metrics"', 'prefix="/api/v1/metrics"')
    p.write_text(c, encoding="utf-8")
    print("[OK] prefix changed to /api/v1/metrics")
else:
    print("[i] already correct")