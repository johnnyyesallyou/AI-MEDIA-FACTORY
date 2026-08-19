import pathlib

p = pathlib.Path("/app/core/cli.py")
c = p.read_text(encoding="utf-8")

# Находим блок stats и заменяем
old_stats = '''        else:  # stats
            loop = FeedbackLoop()
            stats = loop.get_feedback_stats()
            print(f"Feedback loop stats:")
            print(f"  Total posts: {stats['total_posts']}")
            print(f"  Posts with engagement: {stats['posts_with_engagement']}")
            print(f"  Engagement rate: {stats['engagement_rate']:.2%}")'''

new_stats = '''        else:  # stats
            loop = FeedbackLoop()
            stats = loop.get_feedback_stats()
            print("Feedback loop stats:")
            print(f"  Total metrics: {stats['total_metrics']}")
            print(f"  Posts with views: {stats['posts_with_views']}")
            print(f"  Engagement rate: {stats['engagement_rate']:.2%}")
            print(f"  Total views: {stats['total_views']}")
            print(f"  Total likes: {stats['total_likes']}")'''

if old_stats in c:
    c = c.replace(old_stats, new_stats, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] CLI stats fixed")
else:
    print("[i] not found, trying alternative")
    # Альтернатива: ищем просто блок stats
    import re
    pattern = r"        else:  # stats.*?print\(f\"  Engagement rate.*?\"\)"
    if re.search(pattern, c, re.DOTALL):
        c = re.sub(pattern, new_stats, c, count=1, flags=re.DOTALL)
        p.write_text(c, encoding="utf-8")
        print("[OK] CLI stats fixed (regex)")
    else:
        print("[?] Could not find stats block")