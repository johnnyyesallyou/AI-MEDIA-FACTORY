import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { 
  LayoutDashboard, Radio, FileText, Bot, Settings, 
  BarChart3, Brain, FolderOpen, Link2, ScrollText, Wand2, 
  Users, Cog, Menu, X 
, Workflow } from 'lucide-react';
import { DollarSign, Sparkles, FlaskConical } from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/channels', label: 'Channels', icon: Radio },
  { path: '/wizard', label: 'Create Channel', icon: Wand2 },
  { path: '/generate', label: 'Post Generator', icon: Sparkles },
  { path: '/content', label: 'Content', icon: FileText },
  { path: '/ai', label: 'AI Models', icon: Bot },
  { path: '/automation', label: 'Automation', icon: Settings },
  { path: '/workflows', label: 'Workflows', icon: Workflow },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/knowledge', label: 'Knowledge', icon: Brain },
  { path: '/assets', label: 'Assets', icon: FolderOpen },
  { path: '/integrations', label: 'Integrations', icon: Link2 },
  { path: '/logs', label: 'Logs', icon: ScrollText },
  { path: '/users', label: 'Users', icon: Users },
  { path: '/settings', label: 'Settings', icon: Cog },
  { path: '/cost-monitor', label: 'Cost Monitor', icon: DollarSign },
  { path: '/recommendations', label: 'AI Recommendations', icon: Sparkles },
  { path: '/sandbox', label: 'Sandbox', icon: FlaskConical },
];

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-900">
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-gray-800 rounded-lg"
      >
        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      <aside className={`
        fixed lg:static inset-y-0 left-0 z-40
        w-64 bg-gray-800 border-r border-gray-700
        transform transition-transform duration-200 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex items-center justify-center h-16 border-b border-gray-700">
          <h1 className="text-xl font-bold text-white">AI Media Factory</h1>
        </div>
        
        <nav className="mt-4 px-4">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) => `
                flex items-center px-4 py-3 mb-2 rounded-lg transition-colors
                ${isActive 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'}
              `}
            >
              <item.icon size={20} className="mr-3" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="p-6">
          <Outlet />
        </div>
      </main>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default Layout;



