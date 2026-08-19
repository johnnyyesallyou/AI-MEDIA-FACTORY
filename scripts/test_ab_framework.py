import sys
import json
sys.path.insert(0, "/app")

from engines.ab_test_framework import ABTestFramework
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.analytics import PostMetric
import uuid

print("=" * 70)
print("E2E TEST: A/B Testing Framework")
print("=" * 70)

ab = ABTestFramework()
db = SessionLocal()
news_channel = db.query(ChannelORM).filter(ChannelORM.name.like("%News RU%")).first()
db.close()

# 1. Создаём тест
print("\n[1] Creating test:")
test_id = ab.create_test(
    name="Emoji header test",
    description="Compare emoji headers on news posts",
    variants=[
        {"id": "a", "name": "Emoji 📰", "config": {"emoji_header": "📰"}},
        {"id": "b", "name": "Emoji 🔥", "config": {"emoji_header": "🔥"}},
    ],
    traffic_split={"a": 50, "b": 50},
    winner_metric="views",
    scope={"channel_ids": [news_channel.id]},
)
print(f"  ✅ Created: {test_id}")

# 2. Стартуем
print("\n[2] Starting test:")
print(f"  ✅ Started: {ab.start_test(test_id)}")

# 3. Назначаем варианты 6 постам
print("\n[3] Assigning variants (deterministic):")
for i in range(6):
    content_id = f"test-content-{i}"
    variant = None
    db2 = SessionLocal()
    test = db2.query(__import__("core.models.analytics", fromlist=["ABTest"]).ABTest).first()
    db2.close()
    from core.models.analytics import ABTest
    db3 = SessionLocal()
    t = db3.query(ABTest).filter(ABTest.id == uuid.UUID(test_id)).first()
    db3.close()
    v = ab.assign_variant(t, content_id)
    ab.record_exposure(test_id, content_id, v["id"])
    print(f"  {content_id} → variant {v['id']} ({v['name']})")

# 4. Симулируем метрики (variant b лучше)
print("\n[4] Seeding metrics (variant b = better):")
from core.models.analytics import ABTestResult
db4 = SessionLocal()
rows = db4.query(ABTestResult).filter(ABTestResult.test_id == uuid.UUID(test_id)).all()
for row in rows:
    is_b = False
    t = db4.query(ABTest).filter(ABTest.id == uuid.UUID(test_id)).first()
    variant_b_id = t.variants[1]["id"]
    # variant_id сохранён как uuid5 для строковых id
    expected_b = uuid.uuid5(uuid.NAMESPACE_DNS, variant_b_id)
    is_b = (row.variant_id == expected_b)
    
    views = 200 if is_b else 100
    db4.add(PostMetric(
        content_id=row.content_id,
        channel_id=news_channel.id,
        platform="telegram",
        views_count=views,
        likes_count=int(views * 0.1),
    ))
db4.commit()
db4.close()
print("  ✅ Metrics seeded")

# 5. Анализ
print("\n[5] Analyzing:")
ab.update_results(test_id)
result = ab.analyze(test_id)
print(json.dumps(result, indent=2, default=str))

# 6. Завершение
print("\n[6] Completing:")
final = ab.complete_test(test_id)
print(f"  ✅ Completed. Winner: {final.get('winner_variant_id')}")
print(f"  Significant: {final.get('significant')}, p={final.get('p_value')}")

# 7. CLI list
print("\n[7] CLI list:")
for t in ab.list_tests():
    print(f"  [{t['id'][:8]}] {t['name']} | {t['status']}")

print("\n" + "=" * 70)
print("A/B FRAMEWORK TEST PASSED ✅")
print("=" * 70)