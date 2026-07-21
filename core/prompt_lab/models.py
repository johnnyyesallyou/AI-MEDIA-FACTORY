from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TestStatus(str, Enum):
    DRAFT = 'draft'
    RUNNING = 'running'
    COMPLETED = 'completed'

class MetricType(str, Enum):
    CTR = 'ctr'
    ENGAGEMENT_RATE = 'engagement_rate'
    VIEWS = 'views'
    EVALUATOR_SCORE = 'evaluator_score'

class PromptVariant(BaseModel):
    '''
    Конкретная версия промпта, участвующая в тесте.
    '''
    id: str
    name: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ABTestConfig(BaseModel):
    '''
    Конфигурация A/B теста.
    '''
    id: str
    name: str
    task_name: str # Например, 'writing' или 'fact_check'
    variant_a_id: str
    variant_b_id: str
    metric_to_optimize: MetricType = MetricType.CTR
    status: TestStatus = TestStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ABTestResult(BaseModel):
    '''
    Результат A/B теста с определением победителя.
    '''
    id: str
    test_id: str
    variant_a_avg_score: float
    variant_b_avg_score: float
    winning_variant_id: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description='Уверенность в результате (0.0 - 1.0)')
    completed_at: Optional[datetime] = None
