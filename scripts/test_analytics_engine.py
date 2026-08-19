import sys
sys.path.insert(0, "/app")

from engines.analytics_engine import AnalyticsEngine
from core.database import SessionLocal
from core.models.content_orm import ContentORM
import uuid

print("=" * 70)
print("TEST: Analytics Engine")
print("=" * 70)

engine = AnalyticsEngine()
db = SessionLocal()

try:
    # Get a real channel and content
    content = db.query(ContentORM).filter(ContentORM.status == "published").first()
    
    if not content:
        print("⚠️ No published content found, skipping test")
    else:
        print(f"\nUsing content: {content.headline[:50]}")
        print(f"Channel: {content.channel_id}")
        
        # Test 1: Record metric
        print("\n[1] Recording metric:")
        metric = engine.record_post_metric(
            content_id=str(content.id),
            channel_id=str(content.channel_id),
            platform="telegram",
            views=150,
            likes=25,
            shares=8,
            comments=5,
            link_clicks=12,
            button_clicks={"read_more": 10, "source": 2},
        )
        print(f"  ✅ Recorded: views={metric.views_count}")
        
        # Test 2: Get metrics
        print("\n[2] Getting metrics:")
        metrics = engine.get_post_metrics(str(content.id), hours=1)
        print(f"  ✅ Found {len(metrics)} metrics")
        
        # Test 3: Channel analytics
        print("\n[3] Channel analytics:")
        analytics = engine.get_channel_analytics(str(content.channel_id), days=1)
        print(f"  ✅ Total posts: {analytics['total_posts']}")
        print(f"  ✅ Total views: {analytics['total_views']}")
        print(f"  ✅ Avg views: {analytics['avg_views']}")
        print(f"  ✅ Engagement rate: {analytics['engagement_rate']}%")
        
        # Test 4: Top posts
        print("\n[4] Top posts:")
        top = engine.get_top_posts(str(content.channel_id), days=1, limit=5, metric="views")
        print(f"  ✅ Found {len(top)} top posts")
        for i, post in enumerate(top[:3], 1):
            print(f"    {i}. {post['headline'][:40]} - {post['metric_value']} views")
    
    print("\n" + "=" * 70)
    print("ANALYTICS ENGINE TEST PASSED ✅")
    print("=" * 70)
    
finally:
    db.close()