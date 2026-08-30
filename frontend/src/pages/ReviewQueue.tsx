import { useEffect, useState } from 'react';
import { ClipboardCheck, CheckCircle, XCircle, Edit2, Send, Loader2, Video, Image as ImageIcon, FileText, RefreshCw, Save, X } from 'lucide-react';
import { postsAPI, channelsAPI } from '../api/client';

interface Draft {
  id: string;
  channel_id: string | null;
  headline: string;
  text: string | null;
  image_url: string | null;
  video_url: string | null;
  status: string;
  created_at: string | null;
}

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-gray-700 text-gray-300',
  generated: 'bg-blue-900/40 text-blue-300',
  review: 'bg-yellow-900/40 text-yellow-300',
  needs_revision: 'bg-orange-900/40 text-orange-300',
};

export default function ReviewQueue() {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [channels, setChannels] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [busyId, setBusyId] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);

  const load = async () => {
    try {
      setLoading(true);
      const [draftsRes, channelsRes] = await Promise.all([
        postsAPI.listAllDrafts(50),
        channelsAPI.list(),
      ]);
      setDrafts(draftsRes.data || []);
      const list = Array.isArray(channelsRes.data) ? channelsRes.data : (channelsRes.data?.channels || []);
      const map: Record<string, string> = {};
      list.forEach((ch: any) => { map[ch.id] = ch.name; });
      setChannels(map);
    } catch (e: any) {
      setMessage({ type: 'err', text: e.response?.data?.detail || e.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const startEdit = (d: Draft) => {
    setEditingId(d.id);
    setEditText(d.text || '');
  };

  const saveEdit = async (d: Draft) => {
    try {
      setBusyId(d.id);
      await postsAPI.edit(d.id, { text: editText });
      setEditingId(null);
      setMessage({ type: 'ok', text: 'Draft saved' });
      await load();
    } catch (e: any) {
      setMessage({ type: 'err', text: 'Edit error: ' + (e.response?.data?.detail || e.message) });
    } finally {
      setBusyId(null);
    }
  };

  const approveAndPublish = async (d: Draft) => {
    try {
      setBusyId(d.id);
      await postsAPI.approve(d.id);
      await postsAPI.publish(d.id);
      setMessage({ type: 'ok', text: `Published: ${d.headline}` });
      await load();
    } catch (e: any) {
      setMessage({ type: 'err', text: 'Publish error: ' + (e.response?.data?.detail || e.message) });
    } finally {
      setBusyId(null);
    }
  };

  const reject = async (d: Draft) => {
    try {
      setBusyId(d.id);
      await postsAPI.reject(d.id, 'Rejected via Review Queue');
      setMessage({ type: 'ok', text: `Rejected: ${d.headline}` });
      await load();
    } catch (e: any) {
      setMessage({ type: 'err', text: 'Reject error: ' + (e.response?.data?.detail || e.message) });
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <ClipboardCheck className="w-8 h-8 text-yellow-400" />
          <div>
            <h1 className="text-3xl font-bold text-white">Review Queue</h1>
            <p className="text-gray-400 mt-1">{drafts.length} posts waiting for review</p>
          </div>
        </div>
        <button onClick={load} className="p-2 hover:bg-gray-700 rounded-lg" title="Refresh">
          <RefreshCw className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      {message && (
        <div className={`mb-6 p-3 rounded-lg border ${message.type === 'ok' ? 'bg-green-900/30 border-green-700 text-green-200' : 'bg-red-900/30 border-red-700 text-red-200'}`}>
          {message.text}
        </div>
      )}

      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading drafts...</div>
      ) : drafts.length === 0 ? (
        <div className="text-center text-gray-500 py-12">
          <p className="text-lg">No drafts waiting for review</p>
          <p className="text-sm mt-2">Generate a post via Post Generator to see it here</p>
        </div>
      ) : (
        <div className="space-y-4">
          {drafts.map((d) => (
            <div key={d.id} className="bg-gray-800 rounded-lg p-5 border border-gray-700">
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-400">
                    {d.channel_id ? (channels[d.channel_id] || d.channel_id.substring(0, 8)) : 'No channel'}
                  </span>
                  <span className={`px-2 py-0.5 text-xs rounded ${STATUS_STYLES[d.status] || STATUS_STYLES.draft}`}>
                    {d.status}
                  </span>
                  {d.video_url && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded bg-blue-900/30 text-blue-400 border border-blue-800">
                      <Video size={12} /> video
                    </span>
                  )}
                  {d.image_url && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded bg-green-900/30 text-green-400 border border-green-800">
                      <ImageIcon size={12} /> image
                    </span>
                  )}
                </div>
                <span className="text-xs text-gray-500">
                  {d.created_at ? new Date(d.created_at).toLocaleString() : ''}
                </span>
              </div>

              {/* Headline */}
              <h3 className="text-lg font-semibold text-white mb-2">{d.headline}</h3>

              {/* Text / Edit */}
              {editingId === d.id ? (
                <div className="mb-3">
                  <textarea
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    rows={8}
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white text-sm focus:ring-2 focus:ring-yellow-500"
                  />
                </div>
              ) : (
                <div className="mb-3 bg-gray-900 rounded-lg p-3">
                  <p className="text-gray-200 text-sm whitespace-pre-wrap">{d.text || '(no text)'}</p>
                </div>
              )}

              {/* Media preview */}
              {d.image_url && (
                <img src={d.image_url} alt="preview" className="mb-3 max-h-48 rounded-lg border border-gray-700" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
              )}

              {/* Actions */}
              <div className="flex gap-2">
                {editingId === d.id ? (
                  <>
                    <button
                      onClick={() => saveEdit(d)}
                      disabled={busyId === d.id}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                      {busyId === d.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                      Save
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="flex items-center gap-2 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
                    >
                      <X className="w-4 h-4" /> Cancel
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => startEdit(d)}
                      className="flex items-center gap-2 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
                    >
                      <Edit2 className="w-4 h-4" /> Edit
                    </button>
                    <button
                      onClick={() => approveAndPublish(d)}
                      disabled={busyId === d.id}
                      className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      {busyId === d.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                      Approve & Publish
                    </button>
                    <button
                      onClick={() => reject(d)}
                      disabled={busyId === d.id}
                      className="flex items-center gap-2 px-4 py-2 bg-red-700 text-white rounded-lg hover:bg-red-600 disabled:opacity-50"
                    >
                      <XCircle className="w-4 h-4" /> Reject
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}