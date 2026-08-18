import React, { useEffect, useState } from 'react';
import { usersAPI } from '../api/client';
import { Users, Plus, Shield, Mail, Edit2, Trash2, UserCheck } from 'lucide-react';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newUser, setNewUser] = useState({
    email: '',
    full_name: '',
    role: 'viewer',
    password: ''
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await usersAPI.list();
      setUsers(response.data || []);
    } catch (error) {
      console.error('Error loading users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    try {
      await usersAPI.create(newUser);
      setShowCreateModal(false);
      setNewUser({ email: '', full_name: '', role: 'viewer', password: '' });
      loadUsers();
    } catch (error) {
      console.error('Error creating user:', error);
      alert('Ошибка создания пользователя');
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await usersAPI.updateRole(userId, newRole);
      loadUsers();
    } catch (error) {
      console.error('Error updating role:', error);
      alert('Ошибка обновления роли');
    }
  };

  const getRoleBadge = (role: string) => {
    const styles: Record<string, string> = {
      administrator: 'bg-red-500/20 text-red-400 border-red-500/30',
      editor: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      reviewer: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      analyst: 'bg-green-500/20 text-green-400 border-green-500/30',
      viewer: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    };
    const labels: Record<string, string> = {
      administrator: 'Администратор',
      editor: 'Редактор',
      reviewer: 'Ревьюер',
      analyst: 'Аналитик',
      viewer: 'Наблюдатель',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[role] || styles.viewer}`}>
        {labels[role] || role}
      </span>
    );
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'administrator': return <Shield size={16} className="text-red-400" />;
      case 'editor': return <Edit2 size={16} className="text-blue-400" />;
      case 'reviewer': return <UserCheck size={16} className="text-purple-400" />;
      case 'analyst': return <Users size={16} className="text-green-400" />;
      default: return <Users size={16} className="text-gray-400" />;
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Users size={32} className="mr-3 text-blue-400" />
            Users
          </h1>
          <p className="text-gray-400 mt-1">Управление пользователями и ролями</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus size={20} className="mr-2" />
          Добавить пользователя
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Всего пользователей</div>
          <div className="text-2xl font-bold text-white">{users.length}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Активных</div>
          <div className="text-2xl font-bold text-green-400">
            {users.filter(u => u.is_active).length}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Администраторов</div>
          <div className="text-2xl font-bold text-red-400">
            {users.filter(u => u.role === 'administrator').length}
          </div>
        </div>
      </div>

      {/* Users List */}
      {loading ? (
        <div className="text-center text-gray-400 py-12">Загрузка пользователей...</div>
      ) : users.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
          <Users size={48} className="mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold text-white mb-2">Пользователей пока нет</h3>
          <p className="text-gray-400">Добавьте первого пользователя</p>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-900/50 border-b border-gray-700">
              <tr>
                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Пользователь</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Email</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Роль</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Статус</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Создан</th>
                <th className="text-right px-6 py-4 text-sm font-medium text-gray-400">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-700/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold mr-3">
                        {user.full_name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="font-medium text-white">{user.full_name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center text-gray-400">
                      <Mail size={14} className="mr-2" />
                      {user.email}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <select
                      value={user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      className="px-3 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-blue-500"
                    >
                      <option value="administrator">Администратор</option>
                      <option value="editor">Редактор</option>
                      <option value="reviewer">Ревьюер</option>
                      <option value="analyst">Аналитик</option>
                      <option value="viewer">Наблюдатель</option>
                    </select>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs ${user.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                      {user.is_active ? 'Активен' : 'Неактивен'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-400">
                    {new Date(user.created_at).toLocaleDateString('ru-RU')}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-gray-400 hover:text-red-400 transition-colors">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <Plus size={24} className="mr-2" />
              Добавить пользователя
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">Полное имя</label>
                <input
                  type="text"
                  value={newUser.full_name}
                  onChange={(e) => setNewUser({...newUser, full_name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  placeholder="Иван Иванов"
                />
              </div>
              
              <div>
                <label className="block text-gray-400 text-sm mb-2">Email</label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  placeholder="ivan@example.com"
                />
              </div>
              
              <div>
                <label className="block text-gray-400 text-sm mb-2">Пароль</label>
                <input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  placeholder="Минимум 8 символов"
                />
              </div>
              
              <div>
                <label className="block text-gray-400 text-sm mb-2">Роль</label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="viewer">Наблюдатель</option>
                  <option value="editor">Редактор</option>
                  <option value="reviewer">Ревьюер</option>
                  <option value="analyst">Аналитик</option>
                  <option value="administrator">Администратор</option>
                </select>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCreateUser}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Создать
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersPage;
