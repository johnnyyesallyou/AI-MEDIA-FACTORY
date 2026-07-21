from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

class NodeType(str, Enum):
    RESEARCH = 'research'
    DECISION = 'decision'
    BRIEF = 'brief'
    WRITING = 'writing'
    FACT_CHECKER = 'fact_checker'
    EVALUATOR = 'evaluator'
    IMAGE = 'image'
    PUBLISHER = 'publisher'

class NodeStatus(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    SKIPPED = 'skipped'

class WorkflowNode(BaseModel):
    '''
    Отдельный шаг (блок) в пайплайне.
    '''
    id: str
    type: NodeType
    config: Dict[str, Any] = Field(default_factory=dict, description='Настройки узла (например, какая модель используется, какой промпт)')
    status: NodeStatus = NodeStatus.PENDING
    output: Optional[Any] = None

class WorkflowEdge(BaseModel):
    '''
    Связь между двумя узлами (направление потока данных).
    '''
    source_node_id: str
    target_node_id: str

class WorkflowDefinition(BaseModel):
    '''
    Полное описание пайплайна (граф).
    '''
    id: str
    name: str
    description: str = ''
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_start_nodes(self) -> List[WorkflowNode]:
        '''Находит узлы, в которые не входят никакие связи (точки старта).'''
        target_ids = {edge.target_node_id for edge in self.edges}
        return [node for node in self.nodes if node.id not in target_ids]

    def get_next_nodes(self, current_node_id: str) -> List[WorkflowNode]:
        '''Находит следующие узлы для текущего.'''
        next_ids = [edge.target_node_id for edge in self.edges if edge.source_node_id == current_node_id]
        return [node for node in self.nodes if node.id in next_ids]
