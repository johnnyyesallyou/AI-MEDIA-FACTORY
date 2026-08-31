import React, { useState } from 'react';
import { channelControlAPI } from '../api/client';
import { Settings } from 'lucide-react';

interface PublishingModeSelectorProps {
  channelId: string;
  currentMode?: string;
  onModeChange?: (mode: string) => void;
}

export default function PublishingModeSelector({
  channelId,
  currentMode,
  onModeChange,
}: PublishingModeSelectorProps) {
  const [mode, setMode] = useState(currentMode || 'approval_required');
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);

  const handleSave = async () => {
    try {
      setSaving(true);
      await channelControlAPI.setPublishingMode(channelId, mode);
      setEditing(false);
      onModeChange?.(mode);
    } catch (err: any) {
      alert('Failed to save: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSaving(false);
    }
  };

  const modeLabels: Record<string, string> = {
    auto: '🤖 Автоматический',
    approval_required: '👁 Требует подтверждения',
    manual: '✋ Ручной',
  };

  if (!editing) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-gray-400 text-sm">Режим:</span>
        <button
          onClick={() => setEditing(true)}
          className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-300 flex items-center gap-1"
        >
          {modeLabels[mode] || mode}
          <Settings size={12} />
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <select
        value={mode}
        onChange={(e) => setMode(e.target.value)}
        className="px-3 py-1 bg-gray-700 text-gray-300 rounded text-sm border border-gray-600"
        disabled={saving}
      >
        <option value="auto">🤖 Автоматический</option>
        <option value="approval_required">👁 Требует подтверждения</option>
        <option value="manual">✋ Ручной</option>
      </select>
      <button
        onClick={handleSave}
        disabled={saving}
        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded text-sm"
      >
        {saving ? '...' : 'Save'}
      </button>
      <button
        onClick={() => {
          setEditing(false);
          setMode(currentMode || 'approval_required');
        }}
        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded text-sm"
      >
        Cancel
      </button>
    </div>
  );
}