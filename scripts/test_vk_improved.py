import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from engines.analytics import VKEngagementTracker

print("=" * 70)
print("TEST: VKEngagementTracker (improved)")
print("=" * 70)

db = SessionLocal()

vk_channel = db.query(ChannelORM).filter(
    ChannelORM.platform == "vk",
    ChannelORM.vk_access_token != None
).first()

if vk_channel:
    print(f"\nVK Channel: {vk_channel.name}")
    print(f"Group ID: {vk_channel.vk_group_id}")
    
    tracker = VKEngagementTracker(vk_channel.vk_access_token, vk_channel.vk_group_id)
    
    # Тест 1: get_group_stats
    print("\n[1] Testing get_group_stats:")
    stats = tracker.get_group_stats()
    if stats:
        print(f"  ✅ Group name: {stats.get('name')}")
        print(f"  ✅ Members: {stats.get('members_count')}")
    else:
        print("  ⚠️ Could not get group stats")
    
    # Тест 2: get_latest_posts (не требует post_id)
    print("\n[2] Testing get_latest_posts:")
    posts = tracker.get_latest_posts(5)
    if posts:
        print(f"  ✅ Found {len(posts)} posts")
        for i, post in enumerate(posts[:3], 1):
            print(f"\n  Post {i}:")
            print(f"    ID: {post['post_id']}")
            print(f"    Date: {post['date']}")
            print(f"    Text: {post['text'][:60]}...")
            print(f"    Likes: {post['likes']}, Reposts: {post['reposts']}")
            print(f"    Comments: {post['comments']}, Views: {post['views']}")
    else:
        print("  ⚠️ No posts found")
    
    # Тест 3: collect_metrics без post_id
    print("\n[3] Testing collect_metrics (auto mode):")
    metrics = tracker.collect_metrics()
    print(f"  ✅ Collected metrics:")
    print(f"     Group: {metrics.get('group_name')}")
    print(f"     Members: {metrics.get('members_count')}")
    print(f"     Posts: {metrics.get('posts_count')}")
    
else:
    print("⚠️ No VK channel with access_token found")

db.close()
print("\n" + "=" * 70)