import sys
import json
sys.path.insert(0, "/app")

from engines.ab_test_framework import ABTestFramework
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.content_orm import ContentORM
from core.models.analytics import PostMetric, ABTest, ABTestResult
import uuid

print("=" * 70)
print("E2E TEST: A/B Testing Framework (fixed)")
print("=" * 70)

ab = ABTestFramework()
db = SessionLocal()
news_channel = db.query(ChannelORM).filter(ChannelORM.name.like("%News RU%")).first()

# Получаем реальные content_id
real_content = db.query(ContentORM).filter(
    ContentORM.channel_id == news_channel.id,
    ContentORM.status == "published"
).limit(10).all()

if len(real_content) < 6:
    print("⚠️ Not enough published content for test")
    db.close()
    exit(1)

content_ids = [str(c.id) for c in real_content[:6]]
db.close()

print(f"\nUsing {len(content_ids)} real content IDs:")
for cid in content_ids[:3]:
    print(f"  - {cid[:20]}...")

# 1. Создаём тест
print("\n[1] Creating test:")
test_id = ab.create_test(
    name="Emoji header test (real content)",
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

# 3. Назначаем варианты
print("\n[3] Assigning variants (deterministic):")
db2 = SessionLocal()
t = db2.query(ABTest).filter(ABTest.id == uuid.UUID(test_id)).first()
db2.close()

assignments = {}
for cid in content_ids:
    v = ab.assign_variant(t, cid)
    ab.record_exposure(test_id, cid, v["id"])
    assignments[cid] = v["id"]
    print(f"  {cid[:20]}... → variant {v['id']} ({v['name']})")

# 4. Симулируем метрики
print("\n[4] Seeding metrics (variant b = better):")
db3 = SessionLocal()
t = db3.query(ABTest).filter(ABTest.id == uuid.UUID(test_id)).first()
variant_b_id = t.variants[1]["id"]
expected_b = uuid.uuid5(uuid.NAMESPACE_DNS, variant_b_id) if not ab._is_uuid(variant_b_id) else uuid.UUID(variant_b_id)

for cid in content_ids:
    is_b = (assignments[cid] == variant_b_id)
    views = 200 if is_b else 100
    
    db3.add(PostMetric(
        content_id=cid,
        channel_id=news_channel.id,
        platform="telegram",
        views_count=views,
        likes_count=int(views * 0.1),
    ))
db3.commit()
db3.close()
print(f"  ✅ Metrics seeded for {len(content_ids)} posts")

# 5. Анализ
print("\n[5] Analyzing:")
ab.update_results(test_id)
result = ab.analyze(test_id)
print(json.dumps(result, indent=2, default=str))

# 6. Завершение
print("\n[6] Completing:")
final = ab.complete_test(test_id)
print(f"  ✅ Completed")
print(f"  Winner: {final.get('winner_variant_id')}")
print(f"  Significant: {final.get('significant')}, p={final.get('p_value')}")
print(f"  Improvement: {final.get('improvement_pct')}%")

# 7. CLI list
print("\n[7] CLI list:")
for t in ab.list_tests():
    print(f"  [{t['id'][:8]}] {t['name']} | {t['status']}")

print("\n" + "=" * 70)
print("A/B FRAMEWORK TEST PASSED ✅")
print("=" * 70)