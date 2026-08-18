import sys
sys.path.insert(0, '.')

from backend.automation.workflow_engine_v2 import WorkflowEngineV2

print("=" * 80)
print("Тест WorkflowEngineV2")
print("=" * 80)

# Тест 1: Simple workflow (linear)
print("\n1. Simple workflow (A → B → C):")
definition_simple = {
    "id": "test-simple",
    "name": "Test Simple",
    "nodes": [
        {"id": "research", "type": "research", "config": {}, "status": "pending", "output": None},
        {"id": "writing", "type": "writing", "config": {}, "status": "pending", "output": None},
        {"id": "publish", "type": "publish", "config": {}, "status": "pending", "output": None},
    ],
    "edges": [
        {"source_node_id": "research", "target_node_id": "writing"},
        {"source_node_id": "writing", "target_node_id": "publish"},
    ]
}

engine = WorkflowEngineV2(definition_simple)
print(f"   Nodes: {len(engine.nodes)}")
print(f"   Edges: {len(engine.edges)}")
print(f"   Valid: {engine.validate()}")
print(f"   Execution order: {engine.get_execution_order()}")

# Тест 2: Complex workflow (из БД)
print("\n2. Complex workflow (telegram-default):")
definition_complex = {
    "id": "telegram-default",
    "name": "Telegram Research to Publish",
    "nodes": [
        {"id": "research", "type": "research", "config": {}, "status": "pending", "output": None},
        {"id": "decision", "type": "decision", "config": {}, "status": "pending", "output": None},
        {"id": "writing", "type": "brief", "config": {}, "status": "pending", "output": None},
        {"id": "fact_check", "type": "fact_checker", "config": {}, "status": "pending", "output": None},
        {"id": "image", "type": "image", "config": {}, "status": "pending", "output": None},
        {"id": "review", "type": "evaluator", "config": {}, "status": "pending", "output": None},
        {"id": "publisher", "type": "publisher", "config": {}, "status": "pending", "output": None},
    ],
    "edges": [
        {"source_node_id": "research", "target_node_id": "decision"},
        {"source_node_id": "decision", "target_node_id": "writing"},
        {"source_node_id": "writing", "target_node_id": "fact_check"},
        {"source_node_id": "fact_check", "target_node_id": "image"},
        {"source_node_id": "image", "target_node_id": "review"},
        {"source_node_id": "review", "target_node_id": "publisher"},
    ]
}

engine = WorkflowEngineV2(definition_complex)
print(f"   Nodes: {len(engine.nodes)}")
print(f"   Edges: {len(engine.edges)}")
print(f"   Valid: {engine.validate()}")
print(f"   Execution order: {engine.get_execution_order()}")

# Тест 3: Workflow с ветвлением
print("\n3. Branching workflow (A → B, A → C):")
definition_branch = {
    "id": "test-branch",
    "name": "Test Branch",
    "nodes": [
        {"id": "research", "type": "research", "config": {}, "status": "pending", "output": None},
        {"id": "writing", "type": "writing", "config": {}, "status": "pending", "output": None},
        {"id": "image", "type": "image", "config": {}, "status": "pending", "output": None},
        {"id": "publish", "type": "publish", "config": {}, "status": "pending", "output": None},
    ],
    "edges": [
        {"source_node_id": "research", "target_node_id": "writing"},
        {"source_node_id": "research", "target_node_id": "image"},
        {"source_node_id": "writing", "target_node_id": "publish"},
        {"source_node_id": "image", "target_node_id": "publish"},
    ]
}

engine = WorkflowEngineV2(definition_branch)
print(f"   Nodes: {len(engine.nodes)}")
print(f"   Edges: {len(engine.edges)}")
print(f"   Valid: {engine.validate()}")
print(f"   Execution order: {engine.get_execution_order()}")

print("\n✅ Все тесты пройдены!")