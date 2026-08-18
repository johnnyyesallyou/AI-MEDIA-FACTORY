-- Конвертируем workflow из старого формата (stages) в новый (nodes + edges)

-- Функция для конвертации stages в nodes+edges
CREATE OR REPLACE FUNCTION convert_stages_to_graph(stages jsonb)
RETURNS jsonb AS $$
DECLARE
    result jsonb := '{"nodes": [], "edges": []}'::jsonb;
    stage text;
    prev_id text := NULL;
    curr_id text;
    i integer := 0;
BEGIN
    -- Проходим по всем stages
    FOR stage IN SELECT jsonb_array_elements_text(stages)
    LOOP
        curr_id := stage;
        
        -- Добавляем node
        result := jsonb_set(
            result,
            '{nodes}',
            result->'nodes' || jsonb_build_object(
                'id', curr_id,
                'type', curr_id,
                'config', '{}'::jsonb,
                'status', 'pending',
                'output', null
            )
        );
        
        -- Добавляем edge (если это не первый node)
        IF prev_id IS NOT NULL THEN
            result := jsonb_set(
                result,
                '{edges}',
                result->'edges' || jsonb_build_object(
                    'source_node_id', prev_id,
                    'target_node_id', curr_id
                )
            );
        END IF;
        
        prev_id := curr_id;
        i := i + 1;
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Обновляем workflow "Simple" (stages → nodes+edges)
UPDATE workflows
SET definition = convert_stages_to_graph(definition->'stages')
WHERE id = 'wf-simple'
  AND definition ? 'stages'
  AND NOT definition ? 'nodes';

-- Обновляем workflow "Default Full"
UPDATE workflows
SET definition = convert_stages_to_graph(definition->'stages')
WHERE id = 'wf-default-full'
  AND definition ? 'stages'
  AND NOT definition ? 'nodes';

-- Обновляем workflow "Research Only"
UPDATE workflows
SET definition = convert_stages_to_graph(definition->'stages')
WHERE id = 'wf-research-only'
  AND definition ? 'stages'
  AND NOT definition ? 'nodes';

-- Удаляем функцию
DROP FUNCTION IF EXISTS convert_stages_to_graph(jsonb);