import hashlib
from pathlib import Path
from typing import Tuple
from ..models.prompt_tracking import PromptMetadata

class PromptManager:
    def __init__(self, base_dir: str = "prompts"):
        self.base_dir = Path(base_dir)

    def load_prompt(self, category: str, prompt_name: str, version: str = "v1") -> Tuple[str, PromptMetadata]:
        """
        Загружает промпт и его метаданные.
        Пример: load_prompt("writing", "telegram_news", "v2")
        """
        filename = f"{prompt_name}_{version}.md"
        filepath = self.base_dir / category / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Prompt not found: {filepath}")
            
        content = filepath.read_text(encoding="utf-8")
        
        # Вычисляем хэш содержимого, чтобы отлавливать любые изменения в тексте промпта
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        metadata = PromptMetadata(
            category=category,
            name=prompt_name,
            version=version,
            file_path=str(filepath),
            content_hash=content_hash
        )
        
        return content, metadata
