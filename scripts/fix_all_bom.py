import pathlib

files = [
    "/app/engines/source_adapters/remanga_adapter.py",
    "/app/engines/telegraph/publisher.py",
    "/app/backend/automation/jobs/manga_publish_job.py",
    "/app/backend/automation/scheduler.py",
    "/app/backend/automation/jobs/manga_research_job.py",
]

for fpath in files:
    p = pathlib.Path(fpath)
    if not p.exists():
        print(f"SKIP: {fpath} (not found)")
        continue
    
    content = p.read_bytes()
    if content.startswith(b"\xef\xbb\xbf"):
        p.write_bytes(content[3:])
        print(f"? BOM removed: {fpath}")
    else:
        print(f"OK (no BOM): {fpath}")

# ????????? ??? ??? ??????? ????????
import sys
sys.path.insert(0, "/app")

print("\nImport checks:")
try:
    from engines.source_adapters.remanga_adapter import ReMangaAdapter
    adapter = ReMangaAdapter()
    assert hasattr(adapter, "fetch_first_chapter_preview")
    print("? ReMangaAdapter with fetch_first_chapter_preview")
except Exception as e:
    print(f"? ReMangaAdapter: {e}")

try:
    from engines.telegraph.publisher import TelegraphPublisher
    print("? TelegraphPublisher")
except Exception as e:
    print(f"? TelegraphPublisher: {e}")

try:
    from backend.automation.jobs.manga_pipeline_job import MangaPipelineJob
    print("? MangaPipelineJob")
except Exception as e:
    print(f"? MangaPipelineJob: {e}")

try:
    from backend.automation.scheduler import automation_scheduler
    print("? automation_scheduler")
except Exception as e:
    print(f"? automation_scheduler: {e}")
