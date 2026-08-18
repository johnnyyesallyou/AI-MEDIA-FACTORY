import { memo } from 'react';
import { Handle, Position, type Node, type NodeProps } from '@xyflow/react';
import type { WorkflowNodeData, WorkflowNodeType } from '../../types/workflow';

const nodeColors: Record<WorkflowNodeType, { bg: string; border: string; text: string }> = {
  research: { bg: 'bg-blue-900/40', border: 'border-blue-500', text: 'text-blue-300' },
  decision: { bg: 'bg-yellow-900/40', border: 'border-yellow-500', text: 'text-yellow-300' },
  writing: { bg: 'bg-green-900/40', border: 'border-green-500', text: 'text-green-300' },
  evaluation: { bg: 'bg-indigo-900/40', border: 'border-indigo-500', text: 'text-indigo-300' },
  revision: { bg: 'bg-amber-900/40', border: 'border-amber-500', text: 'text-amber-300' },
  re_evaluation: { bg: 'bg-teal-900/40', border: 'border-teal-500', text: 'text-teal-300' },
  publish: { bg: 'bg-red-900/40', border: 'border-red-500', text: 'text-red-300' },
  fact_checker: { bg: 'bg-cyan-900/40', border: 'border-cyan-500', text: 'text-cyan-300' },
  image: { bg: 'bg-purple-900/40', border: 'border-purple-500', text: 'text-purple-300' },
  video: { bg: 'bg-pink-900/40', border: 'border-pink-500', text: 'text-pink-300' },
  voice: { bg: 'bg-orange-900/40', border: 'border-orange-500', text: 'text-orange-300' },
};

type Props = NodeProps<Node<WorkflowNodeData, 'workflowNode'>>;

function WorkflowNode({ data, selected }: Props) {
  const colors = nodeColors[data.nodeType] || nodeColors.writing;

  return (
    <div className={`px-4 py-3 rounded-lg border-2 shadow-lg min-w-[180px] ${colors.bg} ${colors.border} ${selected ? 'ring-2 ring-white ring-offset-2 ring-offset-gray-900' : ''} transition-all duration-200`}>
      <Handle type="target" position={Position.Top} className="!w-3 !h-3 !bg-gray-400 !border-2 !border-gray-700" />
      <div className="flex items-center gap-3">
        <div className={`w-3 h-3 rounded-full ${colors.text} bg-current`} />
        <div>
          <div className={`font-semibold text-sm ${colors.text}`}>{data.label}</div>
          <div className="text-xs text-gray-400 mt-0.5">{data.nodeType}</div>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="!w-3 !h-3 !bg-gray-400 !border-2 !border-gray-700" />
    </div>
  );
}

export default memo(WorkflowNode);