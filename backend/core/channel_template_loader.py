"""Sprint 67.5: Channel Template Library (YAML)."""
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "channel_templates"

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    logger.warning("PyYAML not installed - templates list will be empty-safe")


def list_templates() -> List[Dict[str, Any]]:
    """Загрузить все YAML-шаблоны."""
    result = []
    if HAS_YAML and TEMPLATES_DIR.exists():
        for f in sorted(TEMPLATES_DIR.glob("*.yaml")):
            try:
                data = yaml.safe_load(f.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("name"):
                    result.append(data)
            except Exception as e:
                logger.error(f"Failed to load template {f.name}: {e}")
    if not result:
        logger.warning("No YAML templates loaded")
    return result


def get_template(name: str) -> Optional[Dict[str, Any]]:
    for t in list_templates():
        if t.get("name") == name:
            return t
    return None