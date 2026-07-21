import os
from pathlib import Path
from typing import Optional

class PromptManager:
    def __init__(self, base_dir: str = "prompts"):
        self.base_dir = Path(base_dir)

    def load_prompt(self, category: str, prompt_name: str, version: str = "v1") -> str:
        """
        Загружает промпт из файла.
        Пример: load_prompt("writing", "telegram_news", "v1") 
        -> ищет prompts/writing/telegram_news_v1.md
        """
        filename = f"{prompt_name}_{version}.md"
        filepath = self.base_dir / category / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Prompt not found: {filepath}")
            
        return filepath.read_text(encoding="utf-8")
