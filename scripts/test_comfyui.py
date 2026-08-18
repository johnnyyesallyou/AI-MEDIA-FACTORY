import sys
sys.path.insert(0, "/app")

from engines.comfyui.engine import ComfyUIEngine

engine = ComfyUIEngine()

print("Testing ComfyUI health check...")
healthy = engine._check_health()
print(f"ComfyUI healthy: {healthy}")

if healthy:
    print("\nGenerating test image...")
    result = engine.generate(
        prompt="anime girl, high quality, detailed",
        negative_prompt="low quality, blurry",
        width=512,
        height=512,
        model="flux",
        steps=10
    )
    print(f"Result: {result}")
else:
    print("\nComfyUI not available, testing fallback...")
    result = engine.generate(
        prompt="test prompt",
        width=512,
        height=512
    )
    print(f"Fallback result: {result}")
