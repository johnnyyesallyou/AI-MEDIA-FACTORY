"""
Workflow Engine для AutomationManager v2.

Позволяет конфигурировать workflow (последовательность этапов) для разных каналов.
Workflow хранится в конфигурации, а не жестко прописан в коде.

Примеры workflow:
- Simple: research → writing → evaluation → publish
- Full: research → decision → writing → evaluation → revision → re_evaluation → publish
- Custom: любой набор этапов через from_config()
"""
import logging
from typing import List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class WorkflowStageType(Enum):
    """Типы этапов workflow."""
    RESEARCH = "research"
    DECISION = "decision"
    WRITING = "writing"
    EVALUATION = "evaluation"
    REVISION = "revision"
    RE_EVALUATION = "re_evaluation"
    PUBLISH = "publish"


@dataclass
class WorkflowStage:
    """
    Этап workflow.
    
    Attributes:
        stage_type: тип этапа (research, writing, evaluation, etc.)
        enabled: включен ли этот этап (можно отключать отдельные этапы)
        config: дополнительная конфигурация для этапа (например, model, temperature)
    """
    stage_type: WorkflowStageType
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Валидация после инициализации."""
        if not isinstance(self.stage_type, WorkflowStageType):
            raise ValueError(f"stage_type must be WorkflowStageType, got {type(self.stage_type)}")


@dataclass
class WorkflowDefinition:
    """
    Определение workflow (последовательность этапов).
    
    Workflow можно конфигурировать для разных каналов:
    - Простой: research → writing → publish
    - Полный: research → decision → writing → evaluation → revision → publish
    - Кастомный: любой набор этапов
    
    Attributes:
        name: название workflow
        stages: список этапов в порядке выполнения
        description: описание workflow
    """
    name: str
    stages: List[WorkflowStage]
    description: str = ""
    
    def __post_init__(self):
        """Валидация после инициализации."""
        if not self.stages:
            raise ValueError("Workflow must have at least one stage")
        
        for stage in self.stages:
            if not isinstance(stage, WorkflowStage):
                raise ValueError(f"All stages must be WorkflowStage, got {type(stage)}")
    
    def get_enabled_stages(self) -> List[WorkflowStage]:
        """Возвращает только включенные этапы."""
        return [stage for stage in self.stages if stage.enabled]
    
    def get_stage_names(self) -> List[str]:
        """Возвращает список названий включенных этапов."""
        return [stage.stage_type.value for stage in self.get_enabled_stages()]
    
    @classmethod
    def default(cls) -> "WorkflowDefinition":
        """Создаёт default workflow (полный цикл)."""
        return cls(
            name="default_full_workflow",
            description="Полный цикл: research → decision → writing → evaluation → revision → re_evaluation → publish",
            stages=[
                WorkflowStage(stage_type=WorkflowStageType.RESEARCH),
                WorkflowStage(stage_type=WorkflowStageType.DECISION),
                WorkflowStage(stage_type=WorkflowStageType.WRITING),
                WorkflowStage(stage_type=WorkflowStageType.EVALUATION),
                WorkflowStage(stage_type=WorkflowStageType.REVISION),
                WorkflowStage(stage_type=WorkflowStageType.RE_EVALUATION),
                WorkflowStage(stage_type=WorkflowStageType.PUBLISH),
            ]
        )
    
    @classmethod
    def simple(cls) -> "WorkflowDefinition":
        """Создаёт простой workflow (без decision и revision)."""
        return cls(
            name="simple_workflow",
            description="Простой цикл: research → writing → evaluation → publish",
            stages=[
                WorkflowStage(stage_type=WorkflowStageType.RESEARCH),
                WorkflowStage(stage_type=WorkflowStageType.WRITING),
                WorkflowStage(stage_type=WorkflowStageType.EVALUATION),
                WorkflowStage(stage_type=WorkflowStageType.PUBLISH),
            ]
        )
    
    @classmethod
    def research_only(cls) -> "WorkflowDefinition":
        """Создаёт workflow только для research (без публикации)."""
        return cls(
            name="research_only_workflow",
            description="Только research (без публикации)",
            stages=[
                WorkflowStage(stage_type=WorkflowStageType.RESEARCH),
            ]
        )
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "WorkflowDefinition":
        """
        Создаёт WorkflowDefinition из конфигурации (dict).
        
        Пример config:
        {
            "name": "custom_workflow",
            "description": "Custom workflow for channel X",
            "stages": [
                {"stage_type": "research", "enabled": true},
                {"stage_type": "writing", "enabled": true},
                {"stage_type": "publish", "enabled": false}
            ]
        }
        """
        stages = []
        for stage_config in config.get("stages", []):
            stage_type_str = stage_config.get("stage_type")
            try:
                stage_type = WorkflowStageType(stage_type_str)
            except ValueError:
                logger.warning("Unknown stage type: %s, skipping", stage_type_str)
                continue
            
            stage = WorkflowStage(
                stage_type=stage_type,
                enabled=stage_config.get("enabled", True),
                config=stage_config.get("config", {})
            )
            stages.append(stage)
        
        if not stages:
            logger.warning("No valid stages in config, using default workflow")
            return cls.default()
        
        return cls(
            name=config.get("name", "custom_workflow"),
            description=config.get("description", ""),
            stages=stages
        )
    
    def to_config(self) -> Dict[str, Any]:
        """Конвертирует WorkflowDefinition в конфигурацию (dict)."""
        return {
            "name": self.name,
            "description": self.description,
            "stages": [
                {
                    "stage_type": stage.stage_type.value,
                    "enabled": stage.enabled,
                    "config": stage.config
                }
                for stage in self.stages
            ]
        }