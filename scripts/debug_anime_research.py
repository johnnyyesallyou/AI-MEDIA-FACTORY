import sys
import logging
sys.path.insert(0, "/app")

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

from backend.automation.jobs.anime_research_job import AnimeResearchJob

print("=" * 70)
print("DEBUG: AnimeResearchJob (detailed logging)")
print("=" * 70)

job = AnimeResearchJob()
result = job.run(limit_per_source=5)

print(f"\nResult: {result}")
print("=" * 70)