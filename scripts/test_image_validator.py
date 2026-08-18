import sys, json
sys.path.insert(0, "/app")

from engines.image_validator.engine import ImageValidatorEngine

validator = ImageValidatorEngine()

print("Testing ImageValidator with URL...")
result = validator.validate(
    image_url="https://image.pollinations.ai/prompt/anime%20girl%20high%20quality?width=512&height=512&nologo=true",
    original_prompt="anime girl, high quality",
    context="Anime news illustration"
)

print("\nValidation Result:")
print(json.dumps(result, indent=2))
print(f"\nPassed: {result['passed']}")
