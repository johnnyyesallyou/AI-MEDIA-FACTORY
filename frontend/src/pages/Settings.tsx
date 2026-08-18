import React, { useEffect, useState } from 'react';
import { settingsAPI } from '../api/client';
import { Cog, Globe, Moon, Clock, Database, Key, Shield, Save, RefreshCw, Download } from 'lucide-react';

interface GlobalSettings {
  ui_language: string;
  ui_theme: string;
  timezone: string;
  auto_backup_enabled: boolean;
  backup_cron: string;
  check_updates: boolean;
}

interface EnvVar {
  key: string;
  value_masked: string;
  description: string;
}

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<GlobalSettings | null>(null);
  const [envVars, setEnvVars] = useState<EnvVar[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [backingUp, setBackingUp] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [settingsRes, envRes] = await Promise.all([
        settingsAPI.get(),
        settingsAPI.listEnv(),
      ]);
      setSettings(settingsRes.data);
      setEnvVars(envRes.data || []);
    } catch (error) {
      console.error('Error loading settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      await settingsAPI.update(settings);
      alert('Настройки сохранены!');
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Ошибка сохранения');
    } finally {
      setSaving(false);
    }
  };

  const handleBackup = async () => {
    setBackingUp(true);
    try {
      await settingsAPI.triggerBackup();
      alert('Резервное копирование запущено!');
    } catch (error) {
      console.error('Error triggering backup:', error);
      alert('Ошибка запуска бэкапа');
    } finally {
      setBackingUp(false);
    }
  };

  if (loading) {
    return <div className="text-center text-gray-400 py-12">Загрузка настроек...</div>;
  }

  if (!settings) {
    return <div className="text-center text-red-400 py-12">Ошибка загрузки настроек</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Cog size={32} className="mr-3 text-gray-400" />
            Settings
          </h1>
          <p className="text-gray-400 mt-1">Глобальные настройки системы</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? <RefreshCw size={18} className="mr-2 animate-spin" /> : <Save size={18} className="mr-2" />}
          {saving ? 'Сохранение...' : 'Сохранить'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* UI Settings */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Globe size={20} className="mr-2 text-blue-400" />
            Интерфейс
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-gray-400 text-sm mb-2">Язык интерфейса</label>
              <select
                value={settings.ui_language}
                onChange={(e) => setSettings({...settings, ui_language: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="ru">Русский</option>
                <option value="en">English</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-400 text-sm mb-2">Тема</label>
              <select
                value={settings.ui_theme}
                onChange={(e) => setSettings({...settings, ui_theme: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="dark">Тёмная</option>
                <option value="light">Светлая</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-400 text-sm mb-2">Часовой пояс</label>
              <select
                value={settings.timezone}
                onChange={(e) => setSettings({...settings, timezone: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="Europe/Moscow">Москва (UTC+3)</option>
                <option value="UTC">UTC</option>
                <option value="America/New_York">Нью-Йорк (UTC-5)</option>
                <option value="Asia/Tokyo">Токио (UTC+9)</option>
              </select>
            </div>

            <div className="flex items-center justify-between py-3 border-t border-gray-700">
              <div>
                <div className="font-medium text-white">Проверять обновления</div>
                <div className="text-sm text-gray-400">Автоматически проверять новые версии</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.check_updates}
                  onChange={(e) => setSettings({...settings, check_updates: e.target.checked})}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Backup Settings */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Database size={20} className="mr-2 text-green-400" />
            Резервное копирование
          </h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-gray-700">
              <div>
                <div className="font-medium text-white">Автоматический бэкап</div>
                <div className="text-sm text-gray-400">Создавать резервные копии по расписанию</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.auto_backup_enabled}
                  onChange={(e) => setSettings({...settings, auto_backup_enabled: e.target.checked})}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div>
              <label className="block text-gray-400 text-sm mb-2">Расписание бэкапа (cron)</label>
              <input
                type="text"
                value={settings.backup_cron}
                onChange={(e) => setSettings({...settings, backup_cron: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500 font-mono"
                placeholder="0 3 * * *"
              />
              <p className="text-xs text-gray-500 mt-1">Формат: минута час день месяц день_недели</p>
            </div>

            <button
              onClick={handleBackup}
              disabled={backingUp}
              className="w-full flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {backingUp ? (
                <>
                  <RefreshCw size={18} className="mr-2 animate-spin" />
                  Создание бэкапа...
                </>
              ) : (
                <>
                  <Download size={18} className="mr-2" />
                  Запустить бэкап сейчас
                </>
              )}
            </button>
          </div>
        </div>

        {/* Environment Variables */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 lg:col-span-2">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Key size={20} className="mr-2 text-yellow-400" />
            Переменные окружения
          </h2>
          
          <div className="bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-4 mb-4 flex items-start">
            <Shield size={18} className="text-yellow-400 mr-3 mt-0.5" />
            <div className="text-sm text-yellow-200">
              Значения переменных замаскированы в целях безопасности. Для изменения используйте файл .env или панель управления сервером.
            </div>
          </div>

          <div className="space-y-3">
            {envVars.map((envVar, idx) => (
              <div key={idx} className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-mono text-sm text-blue-400">{envVar.key}</div>
                  <div className="font-mono text-sm text-gray-500">{envVar.value_masked}</div>
                </div>
                {envVar.description && (
                  <div className="text-xs text-gray-400">{envVar.description}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
