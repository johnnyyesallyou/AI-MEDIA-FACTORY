/**
 * Типы для Workflow Designer (Sprint 8.4)
 * Конвертация между React Flow форматом и Backend форматом
 */

import type { Node, Edge } from '@xyflow/react';

// Backend формат (из БД)
export interface BackendNode {
  id: string;
  type: string;
  config: Record<string, any>;
  status: string;
  output: any;
}

export interface BackendEdge {
  source_node_id: string;
  target_node_id: string;
}

export interface BackendWorkflow {
  id: string;
  name: string;
  description: string;
  definition: {
    nodes: BackendNode[];
    edges: BackendEdge[];
    is_active?: boolean;
  };
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Доступные типы нод
export type WorkflowNodeType = 
  | 'research'
  | 'decision'
  | 'writing'
  | 'evaluation'
  | 'revision'
  | 're_evaluation'
  | 'publish'
  | 'fact_checker'
  | 'image'
  | 'video'
  | 'voice';

// Метаданные для каждого типа ноды
export interface NodeTypeMeta {
  type: WorkflowNodeType;
  label: string;
  description: string;
  icon: string;
  color: string;
  category: 'input' | 'process' | 'quality' | 'output';
}

// Палитра нод для sidebar
export const NODE_TYPE_PALETTE: NodeTypeMeta[] = [
  { type: 'research', label: 'Research', description: 'Сбор тем из RSS', icon: 'Rss', color: 'bg-blue-500', category: 'input' },
  { type: 'decision', label: 'Decision', description: 'Выбор тем для публикации', icon: 'Scale', color: 'bg-yellow-500', category: 'input' },
  { type: 'writing', label: 'Writing', description: 'Генерация текста (LLM)', icon: 'PenTool', color: 'bg-green-500', category: 'process' },
  { type: 'image', label: 'Image', description: 'Генерация изображений', icon: 'Image', color: 'bg-purple-500', category: 'process' },
  { type: 'video', label: 'Video', description: 'Генерация видео', icon: 'Video', color: 'bg-pink-500', category: 'process' },
  { type: 'voice', label: 'Voice', description: 'Генерация озвучки', icon: 'Mic', color: 'bg-orange-500', category: 'process' },
  { type: 'evaluation', label: 'Evaluation', description: 'LLM-as-a-Judge', icon: 'Star', color: 'bg-indigo-500', category: 'quality' },
  { type: 'revision', label: 'Revision', description: 'Доработка по замечаниям', icon: 'RefreshCw', color: 'bg-amber-500', category: 'quality' },
  { type: 're_evaluation', label: 'Re-Evaluation', description: 'Повторная оценка', icon: 'CheckCircle2', color: 'bg-teal-500', category: 'quality' },
  { type: 'fact_checker', label: 'Fact Check', description: 'Проверка фактов', icon: 'Shield', color: 'bg-cyan-500', category: 'quality' },
  { type: 'publish', label: 'Publish', description: 'Публикация в Telegram', icon: 'Send', color: 'bg-red-500', category: 'output' },
];

// React Flow Node с кастомными данными (добавлен index signature)
export interface WorkflowNodeData extends Record<string, unknown> {
  label: string;
  nodeType: WorkflowNodeType;
  config: Record<string, any>;
}

export type WorkflowNode = Node<WorkflowNodeData>;

/**
 * Конвертирует Backend формат в React Flow формат
 */
export function backendToFlowNodes(backendNodes: BackendNode[]): WorkflowNode[] {
  return backendNodes.map((node, index) => {
    const meta = NODE_TYPE_PALETTE.find(m => m.type === node.type || m.type === node.type.replace('brief', 'writing'));
    return {
      id: node.id,
      type: 'workflowNode',
      position: { x: 250, y: index * 120 },
      data: {
        label: meta?.label || node.type,
        nodeType: (node.type as WorkflowNodeType) || 'writing',
        config: node.config || {},
      },
    };
  });
}

export function backendToFlowEdges(backendEdges: BackendEdge[]): Edge[] {
  return backendEdges.map((edge, index) => ({
    id: `edge-${index}`,
    source: edge.source_node_id,
    target: edge.target_node_id,
    type: 'smoothstep',
    animated: true,
  }));
}

/**
 * Конвертирует React Flow формат в Backend формат
 */
export function flowToBackendNodes(flowNodes: WorkflowNode[]): BackendNode[] {
  return flowNodes.map(node => ({
    id: node.id,
    type: node.data.nodeType,
    config: node.data.config || {},
    status: 'pending',
    output: null,
  }));
}

export function flowToBackendEdges(flowEdges: Edge[]): BackendEdge[] {
  return flowEdges.map(edge => ({
    source_node_id: edge.source,
    target_node_id: edge.target,
  }));
}

/**
 * Генерирует уникальный ID для новой ноды
 */
export function generateNodeId(nodeType: string): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 7);
  return `${nodeType}-${timestamp}-${random}`;
}