import pathlib, py_compile

p = pathlib.Path('./engines/writing/engine.py')
s = p.read_text(encoding='utf-8')
changes = []

# 1. Добавляем import time (если нет)
if 'import time' not in s:
    s = s.replace('import requests', 'import requests\nimport time', 1)
    changes.append("добавлен import time")

# 2. Заменяем метод _call_llm на версию с retry
old_method = '''    def _call_llm(self, system_prompt: str, user_prompt: str, model: str) -> str:
        """Р’С‹Р·С‹РІР°РµС‚ LLM (СЃРёРЅС…СЂРѕРЅРЅРѕ, РґР»СЏ asyncio.to_thread)."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1024,
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise'''

new_method = '''    def _call_llm(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        model: str,
        max_retries: int = 3,
        base_timeout: int = 300,
    ) -> str:
        """
        Sprint 9: Вызывает LLM с retry-логикой и увеличенным timeout.
        
        - Увеличен timeout: 120s → 300s (5 минут)
        - Добавлена retry-логика: до 3 попыток с экспоненциальным backoff
        - Graceful handling ReadTimeout (Ollama "думает" долго)
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1024,
            }
        }
        
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"LLM call attempt {attempt}/{max_retries} model={model} timeout={base_timeout}s"
                )
                response = requests.post(url, json=payload, timeout=base_timeout)
                response.raise_for_status()
                data = response.json()
                result = data.get("response", "")
                
                if attempt > 1:
                    logger.info(f"LLM call succeeded on attempt {attempt}")
                
                return result
                
            except requests.exceptions.ReadTimeout as e:
                last_error = e
                if attempt < max_retries:
                    # Экспоненциальный backoff: 2, 4, 8 секунд
                    backoff = 2 ** attempt
                    logger.warning(
                        f"LLM ReadTimeout on attempt {attempt}, retrying in {backoff}s: {e}"
                    )
                    time.sleep(backoff)
                else:
                    logger.error(f"LLM ReadTimeout on final attempt {attempt}: {e}")
                    
            except requests.exceptions.ConnectionError as e:
                last_error = e
                if attempt < max_retries:
                    backoff = 2 ** attempt
                    logger.warning(
                        f"LLM ConnectionError on attempt {attempt}, retrying in {backoff}s: {e}"
                    )
                    time.sleep(backoff)
                else:
                    logger.error(f"LLM ConnectionError on final attempt {attempt}: {e}")
                    
            except Exception as e:
                # Для других ошибок (например, 500 Internal Server Error) — не ретраим
                logger.error(f"LLM call failed (non-retryable): {e}")
                raise
        
        # Все попытки провалились
        logger.error(f"LLM call failed after {max_retries} attempts")
        raise last_error'''

if old_method in s:
    s = s.replace(old_method, new_method, 1)
    changes.append("метод _call_llm переписан: timeout 120→300, добавлен retry (3 попытки)")
else:
    print("⚠️ Точный паттерн не найден — показываю текущий метод:")
    lines = s.split('\n')
    for i, line in enumerate(lines):
        if 'def _call_llm' in line:
            for j in range(i, min(i+25, len(lines))):
                print(f"   {j+1}: {lines[j]}")
            break

if changes:
    p.write_text(s, encoding='utf-8')
    print(f"✅ Применено {len(changes)} изменений:")
    for c in changes:
        print(f"   - {c}")
else:
    print("⚠️ Изменения не применены")

# Проверяем синтаксис
print("\n🧪 Проверяем синтаксис...")
try:
    py_compile.compile(str(p), doraise=True)
    print("✅✅✅ СИНТАКСИС ВАЛИДЕН! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")