import sys, json, time
sys.path.insert(0, "/app")

from engines.image_validator.engine import ImageValidatorEngine

print("=" * 60)
print("Testing ImageValidator with llava:7b vision model")
print("=" * 60)

# Создаём валидатор с llava:7b
validator = ImageValidatorEngine(
    ollama_url="http://host.docker.internal:11434",
    model="llava:7b"
)

# Проверяем доступность Ollama
print("\n1. Checking Ollama availability...")
ollama_ok = validator._check_ollama()
print(f"   Ollama available: {ollama_ok}")

if not ollama_ok:
    print("❌ Ollama not available from container")
    print("   Make sure Ollama is running on host and docker has host.docker.internal")
    sys.exit(1)

# Тестируем с реальным изображением из Pollinations
test_image_url = "https://image.pollinations.ai/prompt/anime%20girl%20reading%20book%20in%20library%20high%20quality%20detailed?width=512&height=512&nologo=true"

print("\n2. Testing image validation...")
print(f"   Image URL: {test_image_url}")
print(f"   Original prompt: 'anime girl reading book in library high quality detailed'")
print(f"   Context: 'Anime news illustration'")

start_time = time.time()
result = validator.validate(
    image_url=test_image_url,
    original_prompt="anime girl reading book in library, high quality, detailed",
    context="Anime news illustration"
)
elapsed = time.time() - start_time

print(f"\n3. Validation completed in {elapsed:.2f} seconds")
print("\n" + "=" * 60)
print("VALIDATION RESULT")
print("=" * 60)
print(json.dumps(result, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Quality Score:    {result['quality_score']}/100")
print(f"Prompt Match:     {result['prompt_match']}/100")
print(f"Aesthetic Score:  {result['aesthetic_score']}/100")
print(f"Overall Score:    {result['overall_score']}/100")
print(f"Passed:           {'✅ YES' if result['passed'] else '❌ NO'}")
print(f"Feedback:         {result['feedback']}")
print(f"Source:           {result['source']}")
print("=" * 60)
