import pathlib

# Патчим /ai/models чтобы он читал из Ollama
ai = pathlib.Path('./backend/app/api/v1/ai.py')
s = ai.read_text(encoding='utf-8')

# Ищем эндпоинт list_available_models и заменяем его
old_endpoint = '''@router.get("/models", response_model=List[ModelInfo])
async def list_available_models():
    \'\'\'РџРѕР»СѓС‡РёС‚СЊ СЃРїРёСЃРѕРє РІСЃРµС… РґРѕСЃС‚СѓРїРЅС‹С… LLM РјРѕРґРµР»РµР№.\'\'\'
    return list(_available_models.values())'''

new_endpoint = '''@router.get("/models", response_model=List[ModelInfo])
async def list_available_models():
    \'\'\'Получить список всех доступных LLM моделей из Ollama.\'\'\'
    import requests
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        models = []
        for m in data.get("models", []):
            name = m.get("name", "")
            size_gb = round(m.get("size", 0) / (1024**3), 2)
            models.append(ModelInfo(
                id=name,
                name=name,
                provider="ollama",
                context_window=8192,  # Ollama не отдаёт context_window, ставим дефолт
                is_active=True
            ))
        return models
    except Exception as e:
        # Если Ollama недоступен, возвращаем захардкоженный список
        return list(_available_models.values())'''

if old_endpoint in s:
    s = s.replace(old_endpoint, new_endpoint)
    ai.write_text(s, encoding='utf-8')
    print('OK: /ai/models now reads from Ollama')
else:
    print('WARN: endpoint pattern not found')