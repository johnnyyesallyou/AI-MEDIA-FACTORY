-- Обновляем workflow "Simple" (stages → nodes+edges)
UPDATE workflows
SET definition = '{"nodes": [{"id": "research", "type": "research", "config": {}, "status": "pending", "output": null}, {"id": "writing", "type": "writing", "config": {}, "status": "pending", "output": null}, {"id": "evaluation", "type": "evaluation", "config": {}, "status": "pending", "output": null}, {"id": "publish", "type": "publish", "config": {}, "status": "pending", "output": null}], "edges": [{"source_node_id": "research", "target_node_id": "writing"}, {"source_node_id": "writing", "target_node_id": "evaluation"}, {"source_node_id": "evaluation", "target_node_id": "publish"}]}'::json
WHERE id = 'wf-simple';

-- Обновляем workflow "Default Full"
UPDATE workflows
SET definition = '{"nodes": [{"id": "research", "type": "research", "config": {}, "status": "pending", "output": null}, {"id": "decision", "type": "decision", "config": {}, "status": "pending", "output": null}, {"id": "writing", "type": "writing", "config": {}, "status": "pending", "output": null}, {"id": "evaluation", "type": "evaluation", "config": {}, "status": "pending", "output": null}, {"id": "revision", "type": "revision", "config": {}, "status": "pending", "output": null}, {"id": "re_evaluation", "type": "re_evaluation", "config": {}, "status": "pending", "output": null}, {"id": "publish", "type": "publish", "config": {}, "status": "pending", "output": null}], "edges": [{"source_node_id": "research", "target_node_id": "decision"}, {"source_node_id": "decision", "target_node_id": "writing"}, {"source_node_id": "writing", "target_node_id": "evaluation"}, {"source_node_id": "evaluation", "target_node_id": "revision"}, {"source_node_id": "revision", "target_node_id": "re_evaluation"}, {"source_node_id": "re_evaluation", "target_node_id": "publish"}]}'::json
WHERE id = 'wf-default-full';

-- Обновляем workflow "Research Only"
UPDATE workflows
SET definition = '{"nodes": [{"id": "research", "type": "research", "config": {}, "status": "pending", "output": null}], "edges": []}'::json
WHERE id = 'wf-research-only';