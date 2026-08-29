import { useState, useEffect } from 'react';
import { Sparkles, Send, Loader2, AlertCircle, CheckCircle, Video, Image } from 'lucide-react';
import { channelsAPI, postsAPI } from '../api/client';

interface Channel {
  id: string;
  name: string;
  platform: string;
}

interface Draft {
  id: string;
  text: string;
  media_type: string;
  image_url?: string;
  video_url?: string;
  ready_to_publish: boolean;
}

export default function PostGenerator() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<string>('');
  const [topic, setTopic] = useState('');
  const [contentType, setContentType] = useState('news');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [publishing, setPublishing] = useState(false);
  const [published, setPublished] = useState<any>(null);

  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    try {
      const { data } = await channelsAPI.list();
      const list = Array.isArray(data) ? data : (data.channels || []);
      setChannels(list);
      if (list.length > 0 && !selectedChannel) {
        setSelectedChannel(list[0].id);
      }
    } catch (err: any) {
      setError('Failed to load channels');
    }
  };

  const handleGenerate = async () => {
    if (!selectedChannel || !topic) return;
    try {
      setLoading(true);
      setError(null);
      setDraft(null);
      setPublished(null);
      const { data } = await postsAPI.generate(selectedChannel, { topic, content_type: contentType });
      setDraft(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!draft) return;
    try {
      setPublishing(true);
      setError(null);
      const { data } = await postsAPI.publish(draft.id);
      setPublished(data);
      setDraft(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setPublishing(false);
    }
  };

  const handleRegenerate = () => {
    setDraft(null);
    setPublished(null);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <Sparkles className="w-8 h-8 text-purple-400" />
        <div>
          <h1 className="text-3xl font-bold text-white">Post Generator</h1>
          <p className="text-gray-400 mt-1">Generate and publish posts with AI</p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div className="text-red-200">{error}</div>
        </div>
      )}

      {/* Input form */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Channel</label>
            <select
              value={selectedChannel}
              onChange={(e) => setSelectedChannel(e.target.value)}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
            >
              {channels.map((ch) => (
                <option key={ch.id} value={ch.id}>
                  {ch.name} ({ch.platform})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Content Type</label>
            <select
              value={contentType}
              onChange={(e) => setContentType(e.target.value)}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
            >
              <option value="news">News</option>
              <option value="manga">Manga</option>
              <option value="anime">Anime</option>
            </select>
          </div>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-2">Topic</label>
          <textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Нейросети научились предсказывать погоду"
            rows={2}
            className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
          />
        </div>
        <button
          onClick={handleGenerate}
          disabled={!selectedChannel || !topic || loading}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
          Generate Post
        </button>
      </div>

      {/* Draft preview */}
      {draft && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Generated Draft</h2>
            <div className="flex items-center gap-2">
              {draft.media_type === 'video' && <Video className="w-5 h-5 text-blue-400" />}
              {draft.media_type === 'image' && <Image className="w-5 h-5 text-green-400" />}
              <span className="text-sm text-gray-400">
                {draft.media_type} {draft.ready_to_publish ? '(ready)' : '(not ready)'}
              </span>
            </div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4 mb-4">
            <p className="text-gray-200 whitespace-pre-wrap">{draft.text}</p>
          </div>
          {draft.video_url && (
            <div className="mb-4 p-3 bg-blue-900/20 border border-blue-800 rounded-lg">
              <p className="text-sm text-blue-200">
                <strong>Video:</strong> {draft.video_url.substring(0, 60)}...
              </p>
            </div>
          )}
          {draft.image_url && (
            <div className="mb-4 p-3 bg-green-900/20 border border-green-800 rounded-lg">
              <p className="text-sm text-green-200">
                <strong>Image:</strong> {draft.image_url}
              </p>
            </div>
          )}
          <div className="flex gap-2">
            <button
              onClick={handleRegenerate}
              className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
            >
              Regenerate
            </button>
            <button
              onClick={handlePublish}
              disabled={!draft.ready_to_publish || publishing}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed"
            >
              {publishing ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              Publish to {channels.find(c => c.id === selectedChannel)?.platform}
            </button>
          </div>
        </div>
      )}

      {/* Published confirmation */}
      {published && (
        <div className="bg-gray-800 rounded-lg p-6 border border-green-700">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle className="w-8 h-8 text-green-400" />
            <div>
              <h2 className="text-xl font-semibold text-white">Published Successfully!</h2>
              <p className="text-gray-400 text-sm">
                Message ID: {published.message_id} • {published.published_at}
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              setPublished(null);
              setDraft(null);
              setTopic('');
            }}
            className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Generate Another Post
          </button>
        </div>
      )}
    </div>
  );
}