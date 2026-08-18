import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.analytics import PostMetric, ABTest, ABTestResult
from core.models.content_orm import ContentORM
import uuid

print("=" * 70)
print("TEST: Analytics models (fixed)")
print("=" * 70)

db = SessionLocal()

try:
    # Получаем реальный content для FK
    content = db.query(ContentORM).first()
    if not content:
        print("⚠️ No content in DB, skipping model creation test")
        print("TEST SKIPPED")
        db.close()
        exit(0)
    
    print(f"\nUsing real content: {content.headline[:50]}")
    print(f"Content ID: {content.id}")
    print(f"Channel ID: {content.channel_id}")
    
    # Test 1: Create PostMetric с реальным content_id
    print("\n[1] Creating PostMetric with real content_id:")
    metric = PostMetric(
        content_id=str(content.id),
        channel_id=str(content.channel_id),
        platform="telegram",
        views_count=100,
        likes_count=10,
        shares_count=5,
        comments_count=3,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    print(f"  ✅ Created: id={metric.id}, views={metric.views_count}")
    
    # Test 2: Create ABTest
    print("\n[2] Creating ABTest:")
    test = ABTest(
        name="Test post format",
        description="Compare with/without image",
        variants=[
            {"id": str(uuid.uuid4()), "name": "With image", "config": {"image": True}},
            {"id": str(uuid.uuid4()), "name": "Without image", "config": {"image": False}},
        ],
        traffic_split={
            "variant1": 50,
            "variant2": 50,
        },
        status="running",
    )
    db.add(test)
    db.commit()
    print(f"  ✅ Created: {test.name} (id={test.id})")
    
    # Test 3: Create ABTestResult
    print("\n[3] Creating ABTestResult:")
    result = ABTestResult(
        test_id=test.id,
        content_id=str(content.id),
        variant_id=test.variants[0]["id"],
        impressions=100,
        clicks=25,
        conversions=10,
    )
    db.add(result)
    db.commit()
    print(f"  ✅ Created: impressions={result.impressions}, clicks={result.clicks}")
    
    # Test 4: Query
    print("\n[4] Querying:")
    metrics_count = db.query(PostMetric).count()
    tests_count = db.query(ABTest).count()
    results_count = db.query(ABTestResult).count()
    
    print(f"  ✅ PostMetric count: {metrics_count}")
    print(f"  ✅ ABTest count: {tests_count}")
    print(f"  ✅ ABTestResult count: {results_count}")
    
    # Test 5: Relationship
    print("\n[5] Testing relationships:")
    test_from_db = db.query(ABTest).first()
    print(f"  ✅ ABTest '{test_from_db.name}' has {len(test_from_db.results)} results")
    
    print("\n" + "=" * 70)
    print("ANALYTICS MODELS TEST PASSED ✅")
    print("=" * 70)
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()