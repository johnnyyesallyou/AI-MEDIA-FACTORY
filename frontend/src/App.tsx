import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Channels from './pages/Channels';
import Content from './pages/Content';
import AIModels from './pages/AIModels';
import Automation from './pages/Automation';
import Analytics from './pages/Analytics';
import Knowledge from './pages/Knowledge';
import Assets from './pages/Assets';
import Integrations from './pages/Integrations';
import Logs from './pages/Logs';
import Users from './pages/Users';
import Settings from './pages/Settings';
import CostMonitor from './pages/CostMonitor';
import AIRecommendations from './pages/AIRecommendations';
import Sandbox from './pages/Sandbox';
import Workflows from './pages/Workflows';
import ChannelWizard from './pages/ChannelWizard';
import PostGenerator from './pages/PostGenerator';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="channels" element={<Channels />} />
          <Route path="wizard" element={<ChannelWizard />} />
          <Route path="generate" element={<PostGenerator />} />
          <Route path="content" element={<Content />} />
          <Route path="ai" element={<AIModels />} />
          <Route path="automation" element={<Automation />} />
          <Route path="workflows" element={<Workflows />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="knowledge" element={<Knowledge />} />
          <Route path="assets" element={<Assets />} />
          <Route path="integrations" element={<Integrations />} />
          <Route path="logs" element={<Logs />} />
          <Route path="users" element={<Users />} />
          <Route path="settings" element={<Settings />} />`n          <Route path="cost-monitor" element={<CostMonitor />} />`n          <Route path="recommendations" element={<AIRecommendations />} />`n          <Route path="sandbox" element={<Sandbox />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;



