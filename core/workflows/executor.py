from typing import Dict, Any
from .models import WorkflowDefinition, NodeStatus, WorkflowNode

class WorkflowExecutor:
    '''
    Движок, который умеет обходить граф пайплайна и выполнять узлы.
    В реальности здесь будет асинхронный вызов конкретных движков (engines).
    '''
    
    def __init__(self):
        # В будущем здесь будет Dependency Injection для вызова реальных движков
        pass

    async def execute_node(self, node: WorkflowNode, previous_outputs: Dict[str, Any]) -> Any:
        '''
        Заглушка выполнения конкретного узла.
        '''
        print(f"Выполняется узел: {node.type.value} (ID: {node.id})")
        # Здесь будет логика: if node.type == NodeType.WRITING: return await writing_engine.run(...)
        node.status = NodeStatus.COMPLETED
        return {"mock_output": f"Результат работы {node.type.value}"}

    async def run_workflow(self, workflow: WorkflowDefinition, initial_data: Dict[str, Any] = None):
        '''
        Запускает выполнение всего пайплайна, начиная с узлов-стартеров.
        '''
        print(f"Запуск пайплайна: {workflow.name}")
        
        # Очередь на выполнение (в реальности лучше использовать топологическую сортировку)
        queue = workflow.get_start_nodes()
        executed_outputs: Dict[str, Any] = {}

        while queue:
            current_node = queue.pop(0)
            current_node.status = NodeStatus.RUNNING
            
            try:
                # Выполняем узел
                result = await self.execute_node(current_node, executed_outputs)
                executed_outputs[current_node.id] = result
                current_node.output = result
                
                # Добавляем следующие узлы в очередь
                next_nodes = workflow.get_next_nodes(current_node.id)
                queue.extend(next_nodes)
                
            except Exception as e:
                current_node.status = NodeStatus.FAILED
                print(f"Ошибка в узле {current_node.id}: {e}")
                # В реальности здесь нужна логика обработки ошибок и fallback
        
        print("Пайплайн завершен.")
        return executed_outputs
