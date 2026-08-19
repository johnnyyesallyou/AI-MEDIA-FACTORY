import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.engagement_collection_job import EngagementCollectionJob
from engines.analytics_engine import AnalyticsEngine
from core.database import SessionLocal
from core.models.analytics import PostMetric
import json

print("=" * 70)
print("TEST: EngagementCollectionJob")
print("=" * 70)

# Очищаем старые метрики (опционально)
db = SessionLocal()
count_before = db.query(PostMetric).count()
print(f"\nPostMetrics before: {count_before}")
db.close()

# Запускаем job
job = EngagementCollectionJob()
result = job.run(limit=20, hours_back=168)

print(f"\nResult:")
print(json.dumps(result, indent=2, default=str))

# Проверяем результат
db = SessionLocal()
count_after = db.query(PostMetric).count()
print(f"\nPostMetrics after: {count_after}")
print(f"New metrics added: {count_after - count_before}")

# Последние 5 метрик
recent = db.query(PostMetric).order_by(PostMetric.measured_at.desc()).limit(5).all()
print(f"\nRecent metrics ({len(recent)}):")
for m in recent:
    print(f"  - content_id={m.content_id[:12]}... platform={m.platform} views={m.views_count} likes={m.likes_count}")

db.close()
print("\n" + "=" * 70)