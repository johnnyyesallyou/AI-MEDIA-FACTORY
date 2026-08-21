import pathlib, re

p = pathlib.Path("/app/backend/automation/runtime/job_adapters.py")
c = p.read_text(encoding="utf-8")

if "_maybe_await" not in c:
    helper = '''

async def _maybe_await(r):
    """Sprint 49: async legacy jobs (WritingJob/EvaluatorJob) должны await-иться."""
    import inspect
    if inspect.iscoroutine(r) or inspect.isawaitable(r):
        return await r
    return r

'''
    anchor = "logger = logging.getLogger(__name__)"
    c = c.replace(anchor, anchor + helper, 1)

# Оборачиваем все вызовы legacy jobs
c2, n = re.subn(
    r"result = (job\.run\([^)]*\)|job\.execute\([^)]*\)|job\(context\.channel\))",
    r"result = await _maybe_await(\1)",
    c,
)
if n:
    p.write_text(c2, encoding="utf-8")
    print(f"[OK] {n} job calls wrapped with await")
else:
    print("[!] nothing patched")