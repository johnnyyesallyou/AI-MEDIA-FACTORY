import unittest

from core.workflows.models import WorkflowDefinition, WorkflowNode, WorkflowEdge, NodeType


class WorkflowEngineTest(unittest.TestCase):
    def test_default_workflow_definition_can_be_described_as_data(self):
        workflow = WorkflowDefinition(
            id="telegram-default",
            name="Telegram Research to Publish",
            description="Research -> Decision -> Writing -> Fact Check -> Image -> Review -> Telegram",
            nodes=[
                WorkflowNode(id="research", type=NodeType.RESEARCH),
                WorkflowNode(id="decision", type=NodeType.DECISION),
                WorkflowNode(id="writing", type=NodeType.BRIEF),
                WorkflowNode(id="fact_check", type=NodeType.FACT_CHECKER),
                WorkflowNode(id="image", type=NodeType.IMAGE),
                WorkflowNode(id="review", type=NodeType.EVALUATOR),
                WorkflowNode(id="publisher", type=NodeType.PUBLISHER),
            ],
            edges=[
                WorkflowEdge(source_node_id="research", target_node_id="decision"),
                WorkflowEdge(source_node_id="decision", target_node_id="writing"),
                WorkflowEdge(source_node_id="writing", target_node_id="fact_check"),
                WorkflowEdge(source_node_id="fact_check", target_node_id="image"),
                WorkflowEdge(source_node_id="image", target_node_id="review"),
                WorkflowEdge(source_node_id="review", target_node_id="publisher"),
            ],
        )

        start_nodes = workflow.get_start_nodes()
        self.assertEqual(len(start_nodes), 1)
        self.assertEqual(start_nodes[0].id, "research")

        next_nodes = workflow.get_next_nodes("research")
        self.assertEqual([node.id for node in next_nodes], ["decision"])


if __name__ == "__main__":
    unittest.main()
