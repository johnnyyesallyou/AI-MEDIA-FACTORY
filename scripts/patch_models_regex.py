import pathlib, re

ai = pathlib.Path('./backend/app/api/v1/ai.py')
s = ai.read_text(encoding='utf-8')

# Находим эндпоинт list_available_models и заменяем его тело до следующего @router
pattern = re.compile(
    r'@router\.get\("/models".*?async def list_available_models\(\):.*?(?=@router\.)',
    re.DOTALL
)

new_endpoint = '''@router.get("/models", response_model=List[ModelInfo])
async def list_available_models():
    """Получить живой список моделей из Ollama."""
    import requests
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        resp = requests.get(f"{ollama_url}/api/tags", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        models = []
        for m in data.get("models", []):
            name = m.get("name", "")
            if name:
                models.append(ModelInfo(
                    id=name,
                    name=name,
                    provider="ollama",
                    context_window=8192,
                    is_active=True
                ))
        if models:
            return models
    except Exception:
        pass
    return list(_available_models.values())


'''

if pattern.search(s):
    s = pattern.sub(new_endpoint, s)
    ai.write_text(s, encoding='utf-8')
    print('OK: /ai/models replaced via regex')
else:
    print('ERROR: pattern not found')