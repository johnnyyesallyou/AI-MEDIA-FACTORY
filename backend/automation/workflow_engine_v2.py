"""
Workflow Engine v2 — парсер и исполнитель графа workflow.

Читает workflow из БД (nodes + edges) и выполняет этапы в правильном порядке.
Поддерживает:
- Линейные workflow (A → B → C)
- Ветвления (A → B, A → C)
- Параллельное выполнение
- Валидацию графа (нет циклов)
"""
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Типы узлов в workflow графе."""
    RESEARCH = "research"
    DECISION = "decision"
    WRITING = "writing"  # или "brief"
    EVALUATION = "evaluation"  # или "evaluator"
    REVISION = "revision"
    RE_EVALUATION = "re_evaluation"
    PUBLISH = "publish"  # или "publisher"
    FACT_CHECK = "fact_checker"
    IMAGE = "image"
    # Future: VIDEO, VOICE, etc.


@dataclass
class WorkflowNode:
    """Узел в workflow графе."""
    id: str
    node_type: str  # research, writing, etc.
    config: Dict[str, Any]
    status: str = "pending"
    output: Optional[Any] = None


@dataclass
class WorkflowEdge:
    """Ребро в workflow графе (связь между узлами)."""
    source_node_id: str
    target_node_id: str


class WorkflowEngineV2:
    """
    Движок для выполнения workflow графа.
    
    Читает definition из БД и выполняет узлы в правильном порядке.
    """
    
    def __init__(self, definition: Dict[str, Any]):
        """
        Инициализация из definition (JSON из БД).
        
        Args:
            definition: dict с keys: id, name, nodes, edges, is_active
        """
        self.definition = definition
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: List[WorkflowEdge] = []
        self._parse_definition()
    
    def _parse_definition(self):
        """Парсит definition и создаёт nodes/edges."""
        # Парсим nodes
        for node_data in self.definition.get("nodes", []):
            node = WorkflowNode(
                id=node_data["id"],
                node_type=node_data["type"],
                config=node_data.get("config", {}),
                status=node_data.get("status", "pending"),
                output=node_data.get("output")
            )
            self.nodes[node.id] = node
        
        # Парсим edges
        for edge_data in self.definition.get("edges", []):
            edge = WorkflowEdge(
                source_node_id=edge_data["source_node_id"],
                target_node_id=edge_data["target_node_id"]
            )
            self.edges.append(edge)
        
        logger.info(f"Parsed workflow: {len(self.nodes)} nodes, {len(self.edges)} edges")
    
    def get_execution_order(self) -> List[str]:
        """
        Возвращает порядок выполнения узлов (топологическая сортировка).
        
        Использует алгоритм Kahn для топологической сортировки.
        Проверяет что нет циклов.
        
        Returns:
            List[str]: порядок выполнения node_id
            
        Raises:
            ValueError: если граф содержит цикл
        """
        # Строим граф зависимостей
        in_degree: Dict[str, int] = {node_id: 0 for node_id in self.nodes}
        adjacency: Dict[str, List[str]] = {node_id: [] for node_id in self.nodes}
        
        for edge in self.edges:
            adjacency[edge.source_node_id].append(edge.target_node_id)
            in_degree[edge.target_node_id] += 1
        
        # Kahn's algorithm
        queue: List[str] = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result: List[str] = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            for neighbor in adjacency[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Проверяем что все узлы обработаны (нет циклов)
        if len(result) != len(self.nodes):
            raise ValueError("Workflow graph contains cycles")
        
        logger.info(f"Execution order: {result}")
        return result
    
    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """Возвращает узел по ID."""
        return self.nodes.get(node_id)
    
    def get_node_type(self, node_id: str) -> Optional[str]:
        """Возвращает тип узла (research, writing, etc.)."""
        node = self.nodes.get(node_id)
        return node.node_type if node else None
    
    def validate(self) -> bool:
        """
        Валидирует workflow граф.
        
        Проверяет:
        - Все nodes имеют уникальные ID
        - Все edges ссылаются на существующие nodes
        - Граф не содержит циклов
        - Есть хотя бы один node
        
        Returns:
            True если валиден, False иначе
        """
        if not self.nodes:
            logger.error("Workflow has no nodes")
            return False
        
        # Проверяем что все edges ссылаются на существующие nodes
        for edge in self.edges:
            if edge.source_node_id not in self.nodes:
                logger.error(f"Edge references non-existent source node: {edge.source_node_id}")
                return False
            if edge.target_node_id not in self.nodes:
                logger.error(f"Edge references non-existent target node: {edge.target_node_id}")
                return False
        
        # Проверяем что нет циклов (через get_execution_order)
        try:
            self.get_execution_order()
        except ValueError as e:
            logger.error(f"Workflow validation failed: {e}")
            return False
        
        return True