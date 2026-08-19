import sys
import json
sys.path.insert(0, "/app")

from engines.content_optimization import HeadlineOptimizer, PostingTimeOptimizer

print("=" * 70)
print("E2E TEST: Content Optimization (Sprint 39)")
print("=" * 70)

# 1. Headline Optimizer
print("\n[1] Headline Optimizer:")
hl_opt = HeadlineOptimizer()

headline = "Новый AI агент для автоматизации задач"
result = hl_opt.optimize(headline, platform="telegram")

print(f"  Original: {headline}")
print(f"  Suggestions: {len(result['suggestions'])}")
for s in result['suggestions'][:3]:
    print(f"    - {s}")
print(f"  Variations: {len(result['variations'])}")
for v in result['variations'][:2]:
    print(f"    - {v['headline'][:50]}... ({v['strategy']})")

# 2. Posting Time Optimizer
print("\n[2] Posting Time Optimizer:")
time_opt = PostingTimeOptimizer()

time_result = time_opt.suggest_posting_time(days=30)
print(f"  Best time: {time_result['best_time']}")
print(f"  Reason: {time_result['reason']}")
print(f"  Alternatives: {time_result.get('alternatives', [])}")

# 3. Top headlines analysis
print("\n[3] Top headlines analysis:")
top = hl_opt.analyze_top_headlines(days=30, limit=5)
print(f"  Found {len(top)} top headlines")
for h in top[:3]:
    print(f"    - {h['headline'][:50]}... ({h['metric_value']} views)")

print("\n" + "=" * 70)
print("CONTENT OPTIMIZATION TEST PASSED ✅")
print("=" * 70)