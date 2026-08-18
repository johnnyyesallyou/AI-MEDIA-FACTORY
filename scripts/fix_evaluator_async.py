import pathlib

p = pathlib.Path('./engines/evaluator/engine.py')
s = p.read_text(encoding='utf-8')
changed = []

# 1. Добавляем import asyncio
if 'import asyncio' not in s:
    s = s.replace('import os\nimport json', 'import os\nimport json\nimport asyncio', 1)
    if 'import asyncio' not in s:
        s = 'import asyncio\n' + s
    changed.append('import_asyncio')

# 2. Переименовываем async def evaluate -> def evaluate_sync
old_sig = '''    async def evaluate(
        self,
        source_facts: str,
        generated_post: str,
        target_style: str
    ) -> EvaluationResult:
        """Оценивает пост через реальный LLM с fallback на эвристику."""'''

new_sig = '''    def evaluate_sync(
        self,
        source_facts: str,
        generated_post: str,
        target_style: str
    ) -> EvaluationResult:
        """Синхронная оценка поста через реальный LLM с fallback на эвристику."""'''

if old_sig in s:
    s = s.replace(old_sig, new_sig)
    changed.append('evaluate_sync')

# 3. Добавляем async-обёртку evaluate, которая уходит в thread pool (не блокирует event loop!)
if 'async def evaluate(' not in s:
    wrapper = '''
    async def evaluate(
        self,
        source_facts: str,
        generated_post: str,
        target_style: str
    ) -> EvaluationResult:
        """
        Async-обёртка: выполняет синхронную оценку в thread pool.
        КРИТИЧНО: не блокирует event loop uvicorn, пока LLM отвечает 5-10 сек.
        """
        return await asyncio.to_thread(
            self.evaluate_sync,
            source_facts,
            generated_post,
            target_style
        )
'''
    # Вставляем перед _call_llm
    if '    def _call_llm(' in s:
        s = s.replace('    def _call_llm(', wrapper + '\n    def _call_llm(', 1)
        changed.append('async_wrapper')

p.write_text(s, encoding='utf-8')
print(f'OK: evaluator patched: {", ".join(changed)}')