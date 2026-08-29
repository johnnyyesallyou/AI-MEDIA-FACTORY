import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, BarChart3, FileText, Video, Image, Clock } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { channelsAPI, postsAPI } from '../api/client';

interface PostHistory {
  id: string;
  channel_id: string;
  platform: string;
  text: string | null;
  image_url: string | null;
  video_url: string | null;
  media_type: string;
  message_id: string | null;
  posted_at: string;
}

interface ChannelMetrics {
  channel_id: string;
  period_days: number;
  total_posts: number;
  total_views: number;
  total_likes: number;
  avg_views_per_post: number;
  avg_likes_per_post: number;
  top_patterns: string[];
}

const COLORS = ['#3b82f6', '#10b981', '#6b7280'];

export default function ChannelAnalytics() {
  const { id } = useParams<{ id: string }>();
  const [channel, setChannel] = useState<any>(null);
  const [posts, setPosts] = useState<PostHistory[]>([]);
  const [metrics, setMetrics] = useState<ChannelMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [channelRes, postsRes, metricsRes] = await Promise.all([
        channelsAPI.get(id!),
        postsAPI.getHistory(id!, 50),
        postsAPI.getMetrics(id!, 30),
      ]);
      
      setChannel(channelRes.data);
      setPosts(postsRes.data);
      setMetrics(metricsRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Compute media distribution
  const mediaStats = {
    video: posts.filter(p => p.media_type === 'video').length,
    image: posts.filter(p => p.media_type === 'image').length,
    none: posts.filter(p => p.media_type === 'none' || !p.media_type).length,
  };

  const pieData = [
    { name: 'Video', value: mediaStats.video },
    { name: 'Image', value: mediaStats.image },
    { name: 'Text only', value: mediaStats.none },
  ].filter(d => d.value > 0);

  if (loading) {
    return <div className="text-center text-gray-400 py-12">Loading analytics...</div>;
  }

  if (error) {
    return <div className="text-center text-red-400 py-12">Error: {error}</div>;
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link to="/channels" className="p-2 hover:bg-gray-700 rounded-lg">
          <ArrowLeft className="w-5 h-5 text-gray-400" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white">
            {channel?.name || 'Channel'} Analytics
          </h1>
          <p className="text-gray-400 mt-1">
            {channel?.platform} • {channel?.content_type} • Last 30 days
          </p>
        </div>
      </div>

      {/* Overview cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatCard icon={FileText} label="Total Posts" value={metrics?.total_posts || 0} />
        <StatCard icon={Video} label="Video Posts" value={mediaStats.video} color="blue" />
        <StatCard icon={Image} label="Image Posts" value={mediaStats.image} color="green" />
        <StatCard icon={Clock} label="Last Post" value={posts[0] ? new Date(posts[0].posted_at).toLocaleDateString() : '—'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Media Distribution */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-purple-400" />
            Media Distribution
          </h2>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-500 py-12">No posts yet</div>
          )}
        </div>

        {/* Top Patterns */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">💡</span>
            What Works (Learning Loop)
          </h2>
          {metrics?.top_patterns && metrics.top_patterns.length > 0 ? (
            <ul className="space-y-2">
              {metrics.top_patterns.map((p, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="text-green-400">✓</span>
                  <span>{p}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-500 text-sm">
              <p>No patterns detected yet.</p>
              <p className="mt-2 text-xs">Learning Loop requires more published posts with engagement metrics to identify patterns.</p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Posts */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-400" />
          Recent Posts ({posts.length})
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-gray-700">
              <tr className="text-gray-400">
                <th className="text-left py-2 px-3">Date</th>
                <th className="text-left py-2 px-3">Media</th>
                <th className="text-left py-2 px-3">Content</th>
                <th className="text-left py-2 px-3">Message ID</th>
              </tr>
            </thead>
            <tbody>
              {posts.slice(0, 20).map((post) => (
                <tr key={post.id} className="border-b border-gray-700 hover:bg-gray-700/30">
                  <td className="py-3 px-3 text-gray-400 whitespace-nowrap">
                    {new Date(post.posted_at).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-3">
                    <MediaBadge type={post.media_type} />
                  </td>
                  <td className="py-3 px-3 text-gray-200 max-w-md">
                    <div className="truncate">{post.text || '(no text)'}</div>
                  </td>
                  <td className="py-3 px-3 text-gray-500 font-mono text-xs">
                    {post.message_id || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {posts.length === 0 && (
            <div className="text-center text-gray-500 py-8">No posts yet</div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color = 'gray' }: any) {
  const colorMap: any = {
    gray: 'text-gray-400',
    blue: 'text-blue-400',
    green: 'text-green-400',
  };
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center gap-3 mb-2">
        <Icon className={`w-5 h-5 ${colorMap[color]}`} />
        <span className="text-sm text-gray-400">{label}</span>
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
    </div>
  );
}

function MediaBadge({ type }: { type: string }) {
  const styles: any = {
    video: 'bg-blue-900/30 text-blue-400 border-blue-800',
    image: 'bg-green-900/30 text-green-400 border-green-800',
    none: 'bg-gray-700 text-gray-400 border-gray-600',
  };
  const icons: any = {
    video: <Video size={12} />,
    image: <Image size={12} />,
    none: <FileText size={12} />,
  };
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded border ${styles[type] || styles.none}`}>
      {icons[type] || icons.none}
      {type || 'none'}
    </span>
  );
}