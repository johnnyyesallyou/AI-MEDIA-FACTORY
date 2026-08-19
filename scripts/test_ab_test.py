import sys, json
sys.path.insert(0, "/app")

from engines.ab_test.engine import ABTestEngine

print("=" * 60)
print("Testing A/B Testing Engine")
print("=" * 60)

ab_engine = ABTestEngine(num_variants=2)  # 2 варианта для скорости

print("\nGenerating 2 variants and selecting best...")
print("Prompt: 'anime warrior with sword, epic battle scene'")

result = ab_engine.generate_and_select(
    prompt="anime warrior with sword, epic battle scene, high quality",
    negative_prompt="low quality, blurry, text",
    width=512,
    height=512,
    num_variants=2
)

print("\n" + "=" * 60)
print("A/B TEST RESULT")
print("=" * 60)
print(f"Variants generated: {result['num_generated']}")
print(f"Variants passed:    {result['num_passed']}")
print(f"Selection reason:   {result['selection_reason']}")

if result['best_variant']:
    best = result['best_variant']
    print(f"\nBest variant: #{best['variant_id']}")
    print(f"  Score: {best['overall_score']}/100")
    print(f"  Quality: {best['validation']['quality_score']}/100")
    print(f"  Prompt match: {best['validation']['prompt_match']}/100")
    print(f"  Aesthetic: {best['validation']['aesthetic_score']}/100")
    print(f"  Image path: {best.get('image_path', 'N/A')}")

print("\nAll variants:")
for v in result['all_variants']:
    print(f"  Variant #{v['variant_id']}: score={v['overall_score']}, seed={v['seed']}")

print("=" * 60)
