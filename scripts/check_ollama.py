import requests
try:
    r = requests.post(
        "http://host.docker.internal:11434/api/generate",
        json={
            "model": "gemma2:9b",
            "prompt": "Переведи на русский язык, только перевод без пояснений: OpenAI releases its official report on the Hugging Face breach",
            "stream": False,
            "options": {"temperature": 0.3}
        },
        timeout=120,
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print(f"Response: {r.json().get('response', '')[:150]}")
    else:
        print(f"Error body: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")