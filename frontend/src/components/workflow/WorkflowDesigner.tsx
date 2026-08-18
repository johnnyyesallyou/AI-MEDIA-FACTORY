import { useState, useCallback, useRef, useMemo } from 'react';
import {
  ReactFlow,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  Panel,
  ReactFlowProvider,
  useReactFlow,
  BackgroundVariant,
  type Connection,
  type NodeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import * as Icons from 'lucide-react';

import WorkflowNodeComponent from './WorkflowNode';
import {
  backendToFlowNodes,
  backendToFlowEdges,
  flowToBackendNodes,
  flowToBackendEdges,
  generateNodeId,
  NODE_TYPE_PALETTE,
} from '../../types/workflow';
import type { WorkflowNode as WNode, WorkflowNodeType, BackendWorkflow } from '../../types/workflow';

const nodeTypes = { workflowNode: WorkflowNodeComponent } as unknown as NodeTypes;

function getIcon(name: string): React.ComponentType<any> {
  const lib: any = Icons;
  return lib[name] || lib.Box || (() => null);
}

const SaveIcon: any = (Icons as any).Save || (() => null);
const PlayIcon: any = (Icons as any).Play || (() => null);
const TrashIcon: any = (Icons as any).Trash2 || (() => null);
const PlusIcon: any = (Icons as any).Plus || (() => null);

interface WorkflowDesignerProps {
  initialWorkflow?: BackendWorkflow;
  onSave: (data: { name: string; description: string; definition: any }) => void;
  onRun?: () => void;
  isSaving?: boolean;
}

function DesignerInner({ initialWorkflow, onSave, onRun, isSaving }: WorkflowDesignerProps) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();

  const initialNodes = useMemo(() => {
    if (initialWorkflow?.definition?.nodes) {
      return backendToFlowNodes(initialWorkflow.definition.nodes);
    }
    return [];
  }, [initialWorkflow]);

  const initialEdges = useMemo(() => {
    if (initialWorkflow?.definition?.edges) {
      return backendToFlowEdges(initialWorkflow.definition.edges);
    }
    return [];
  }, [initialWorkflow]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes as any);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [workflowName, setWorkflowName] = useState(initialWorkflow?.name || 'Новый Workflow');
  const [workflowDescription, setWorkflowDescription] = useState(initialWorkflow?.description || '');
  const [selectedNode, setSelectedNode] = useState<WNode | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge({ ...connection, type: 'smoothstep', animated: true }, eds));
    },
    [setEdges]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData('application/reactflow-type') as WorkflowNodeType;
      if (!type) return;
      const bounds = reactFlowWrapper.current?.getBoundingClientRect();
      if (!bounds) return;
      const position = screenToFlowPosition({
        x: event.clientX - bounds.left,
        y: event.clientY - bounds.top,
      });
      const meta = NODE_TYPE_PALETTE.find((p) => p.type === type);
      const newNode: WNode = {
        id: generateNodeId(type),
        type: 'workflowNode',
        position,
        data: { label: meta?.label || type, nodeType: type, config: {} },
      };
      setNodes((nds: any[]) => nds.concat(newNode as any));
    },
    [screenToFlowPosition, setNodes]
  );

  const onNodeClick = useCallback((_: any, node: any) => setSelectedNode(node as WNode), []);
  const onPaneClick = useCallback(() => setSelectedNode(null), []);

  const updateNodeConfig = useCallback(
    (key: string, value: any) => {
      if (!selectedNode) return;
      setNodes((nds: any[]) =>
        nds.map((n: any) =>
          n.id === selectedNode.id
            ? { ...n, data: { ...n.data, config: { ...(n.data.config || {}), [key]: value } } }
            : n
        )
      );
      setSelectedNode((prev: WNode | null) =>
        prev ? { ...prev, data: { ...prev.data, config: { ...(prev.data.config || {}), [key]: value } } } : null
      );
    },
    [selectedNode, setNodes]
  );

  const deleteSelectedNode = useCallback(() => {
    if (!selectedNode) return;
    const id = selectedNode.id;
    setNodes((nds: any[]) => nds.filter((n: any) => n.id !== id));
    setEdges((eds) => eds.filter((e) => e.source !== id && e.target !== id));
    setSelectedNode(null);
  }, [selectedNode, setNodes, setEdges]);

  const validate = useCallback((): string[] => {
    const errors: string[] = [];
    if (nodes.length === 0) {
      errors.push('Workflow не содержит нод');
      return errors;
    }
    const adjacency = new Map<string, string[]>();
    (nodes as any[]).forEach((n) => adjacency.set(n.id, []));
    edges.forEach((e) => {
      adjacency.get(e.source)?.push(e.target);
    });
    const visited = new Set<string>();
    const stack = new Set<string>();
    const hasCycle = (nodeId: string): boolean => {
      if (stack.has(nodeId)) return true;
      if (visited.has(nodeId)) return false;
      visited.add(nodeId);
      stack.add(nodeId);
      for (const neighbor of adjacency.get(nodeId) || []) {
        if (hasCycle(neighbor)) return true;
      }
      stack.delete(nodeId);
      return false;
    };
    for (const node of nodes as any[]) {
      if (hasCycle(node.id)) {
        errors.push('Граф содержит цикл');
        break;
      }
    }
    const connected = new Set<string>();
    edges.forEach((e) => {
      connected.add(e.source);
      connected.add(e.target);
    });
    if (nodes.length > 1) {
      (nodes as any[]).forEach((n) => {
        if (!connected.has(n.id)) errors.push(`Нода "${n.data.label}" оторвана от графа`);
      });
    }
    const hasPublish = (nodes as any[]).some((n) => n.data.nodeType === 'publish');
    if (!hasPublish) errors.push('Предупреждение: нет ноды Publish — контент не будет опубликован');
    return errors;
  }, [nodes, edges]);

  const handleSave = useCallback(() => {
    const errors = validate();
    setValidationErrors(errors);
    if (errors.some((e) => e.includes('цикл'))) {
      alert('Невозможно сохранить: граф содержит цикл!');
      return;
    }
    onSave({
      name: workflowName,
      description: workflowDescription,
      definition: {
        nodes: flowToBackendNodes(nodes as WNode[]),
        edges: flowToBackendEdges(edges),
        is_active: true,
      },
    });
  }, [nodes, edges, workflowName, workflowDescription, validate, onSave]);

  const groupedPalette = useMemo(() => {
    const groups: Record<string, typeof NODE_TYPE_PALETTE> = { input: [], process: [], quality: [], output: [] };
    NODE_TYPE_PALETTE.forEach((item) => groups[item.category].push(item));
    return groups;
  }, []);

  const categoryLabels: Record<string, string> = {
    input: '📥 Вход',
    process: '⚙️ Обработка',
    quality: '✅ Качество',
    output: '🚀 Выход',
  };

  return (
    <div className="flex h-[calc(100vh-120px)] bg-gray-900 text-white">
      {/* Палитра */}
      <div className="w-64 bg-gray-800 border-r border-gray-700 overflow-y-auto flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wide">Палитра нод</h3>
          <p className="text-xs text-gray-500 mt-1">Перетащите на canvas</p>
        </div>
        <div className="flex-1 p-3 space-y-4">
          {Object.entries(groupedPalette).map(([category, items]) => (
            <div key={category}>
              <div className="text-xs font-semibold text-gray-400 mb-2 px-1">{categoryLabels[category]}</div>
              <div className="space-y-1.5">
                {items.map((item) => {
                  const Icon = getIcon(item.icon);
                  return (
                    <div
                      key={item.type}
                      draggable
                      onDragStart={(e) => {
                        e.dataTransfer.setData('application/reactflow-type', item.type);
                        e.dataTransfer.effectAllowed = 'move';
                      }}
                      className="flex items-center gap-2 px-3 py-2 bg-gray-700/50 hover:bg-gray-700 border border-gray-600 rounded-md cursor-grab active:cursor-grabbing transition-colors"
                      title={item.description}
                    >
                      <Icon className="w-4 h-4 text-gray-300" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate">{item.label}</div>
                        <div className="text-xs text-gray-500 truncate">{item.description}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 flex flex-col">
        <div className="h-14 bg-gray-800 border-b border-gray-700 px-4 flex items-center gap-3">
          <input
            type="text"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm flex-1 max-w-xs focus:outline-none focus:border-blue-500"
            placeholder="Название workflow"
          />
          <div className="flex-1" />
          {validationErrors.length > 0 && (
            <div className="text-xs text-amber-400 mr-2 max-w-md truncate" title={validationErrors.join('\n')}>
              ⚠️ {validationErrors.length} предупрежд.
            </div>
          )}
          {onRun && (
            <button onClick={onRun} className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded text-sm font-medium transition-colors">
              <PlayIcon className="w-4 h-4" /> Запуск
            </button>
          )}
          <button onClick={handleSave} disabled={isSaving} className="flex items-center gap-1.5 px-4 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded text-sm font-medium transition-colors">
            <SaveIcon className="w-4 h-4" /> {isSaving ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>

        <div className="flex-1" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes as any}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            fitView
            className="bg-gray-900"
            defaultEdgeOptions={{ type: 'smoothstep', animated: true }}
          >
            <Controls />
            <MiniMap
              nodeColor={(n: any) => {
                const colors: Record<string, string> = {
                  research: '#3b82f6', decision: '#eab308', writing: '#22c55e', evaluation: '#6366f1',
                  revision: '#f59e0b', re_evaluation: '#14b8a6', publish: '#ef4444', fact_checker: '#06b6d4',
                  image: '#a855f7', video: '#ec4899', voice: '#f97316',
                };
                return colors[n.data?.nodeType as string] || '#6b7280';
              }}
            />
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#374151" />
            {nodes.length === 0 && (
              <Panel position="top-center">
                <div className="bg-gray-800/90 border border-gray-700 rounded-lg px-6 py-4 text-center mt-20">
                  <PlusIcon className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">Перетащите ноды из палитры слева, чтобы начать</p>
                </div>
              </Panel>
            )}
          </ReactFlow>
        </div>
      </div>

      {/* Inspector */}
      <div className="w-80 bg-gray-800 border-l border-gray-700 overflow-y-auto">
        {selectedNode ? (
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wide">Свойства ноды</h3>
              <button onClick={deleteSelectedNode} className="p-1.5 hover:bg-red-600/20 rounded text-red-400" title="Удалить ноду">
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Тип</label>
                <div className="bg-gray-700 px-3 py-2 rounded text-sm font-mono">{selectedNode.data.nodeType}</div>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">ID</label>
                <div className="bg-gray-700 px-3 py-2 rounded text-xs font-mono truncate">{selectedNode.id}</div>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Название</label>
                <input
                  type="text"
                  value={selectedNode.data.label}
                  onChange={(e) => {
                    const newLabel = e.target.value;
                    setNodes((nds: any[]) =>
                      nds.map((n: any) => (n.id === selectedNode.id ? { ...n, data: { ...n.data, label: newLabel } } : n))
                    );
                    setSelectedNode((prev: WNode | null) => (prev ? { ...prev, data: { ...prev.data, label: newLabel } } : null));
                  }}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="pt-4 border-t border-gray-700">
                <h4 className="text-xs font-semibold text-gray-400 mb-3 uppercase tracking-wide">Конфигурация</h4>
                {selectedNode.data.nodeType === 'research' && (
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Максимум тем</label>
                    <input
                      type="number"
                      value={selectedNode.data.config.max_topics || 10}
                      onChange={(e) => updateNodeConfig('max_topics', parseInt(e.target.value))}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm"
                    />
                  </div>
                )}
                {selectedNode.data.nodeType === 'writing' && (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">Модель</label>
                      <select
                        value={selectedNode.data.config.model || 'llama3.1:8b'}
                        onChange={(e) => updateNodeConfig('model', e.target.value)}
                        className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm"
                      >
                        <option value="llama3.1:8b">llama3.1:8b</option>
                        <option value="mistral-nemo:12b">mistral-nemo:12b</option>
                        <option value="qwen2.5:14b">qwen2.5:14b</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">Temperature: {selectedNode.data.config.temperature || 0.7}</label>
                      <input
                        type="range" min="0" max="1" step="0.1"
                        value={selectedNode.data.config.temperature || 0.7}
                        onChange={(e) => updateNodeConfig('temperature', parseFloat(e.target.value))}
                        className="w-full"
                      />
                    </div>
                  </div>
                )}
                {selectedNode.data.nodeType === 'evaluation' && (
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Минимальный score</label>
                    <input
                      type="number" min="0" max="100"
                      value={selectedNode.data.config.min_score || 70}
                      onChange={(e) => updateNodeConfig('min_score', parseInt(e.target.value))}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm"
                    />
                  </div>
                )}
                {selectedNode.data.nodeType === 'publish' && (
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedNode.data.config.auto_publish ?? true}
                      onChange={(e) => updateNodeConfig('auto_publish', e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-gray-300">Авто-публикация</span>
                  </label>
                )}
                {!['research', 'writing', 'evaluation', 'publish'].includes(selectedNode.data.nodeType) && (
                  <div className="text-xs text-gray-500 italic">Нет специфичных настроек для этого типа</div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4">
            <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wide mb-4">Workflow</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Описание</label>
                <textarea
                  value={workflowDescription}
                  onChange={(e) => setWorkflowDescription(e.target.value)}
                  rows={3}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-sm resize-none"
                  placeholder="Опишите назначение workflow..."
                />
              </div>
              <div className="pt-4 border-t border-gray-700">
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between"><span className="text-gray-400">Нод:</span><span className="font-mono">{nodes.length}</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">Связей:</span><span className="font-mono">{edges.length}</span></div>
                </div>
              </div>
              {validationErrors.length > 0 && (
                <div className="pt-4 border-t border-gray-700">
                  <h4 className="text-xs font-semibold text-amber-400 mb-2 uppercase tracking-wide">⚠️ Предупреждения</h4>
                  <ul className="space-y-1 text-xs text-amber-300">
                    {validationErrors.map((err, i) => (<li key={i}>• {err}</li>))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function WorkflowDesigner(props: WorkflowDesignerProps) {
  return (
    <ReactFlowProvider>
      <DesignerInner {...props} />
    </ReactFlowProvider>
  );
}