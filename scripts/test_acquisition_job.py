import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.smart_image_acquisition_job import SmartImageAcquisitionJob
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

print("=" * 70)
print("TEST: SmartImageAcquisitionJob")
print("=" * 70)

db = SessionLocal()
job = SmartImageAcquisitionJob()

# Тест на manga канал
manga_channel = db.query(ChannelORM).filter(ChannelORM.name.like("%Манга%")).first()

print(f"\nProcessing manga channel: {manga_channel.name}")
result = job.run(channel=manga_channel, limit=5)

print(f"\nResult:")
print(f"  Processed: {result.get('processed')}")
print(f"  Resolved: {result.get('resolved')}")
print(f"  Success rate: {result.get('success_rate', 0):.1%}")
print(f"  Sources: {result.get('sources')}")

db.close()
print("=" * 70)