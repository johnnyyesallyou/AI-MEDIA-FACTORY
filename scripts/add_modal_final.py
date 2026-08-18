import pathlib

f = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = f.read_text(encoding='utf-8')

if 'showPlatformModal &&' in s:
    print("✅ Модалка showPlatformModal уже есть в JSX")
else:
    print("⚠️ Модалки нет — добавляем перед 'Modal for schedule'")
    
    platform_modal = '''      {/* Sprint 11: Modal for VK/YouTube/Dzen connection */}
      {showPlatformModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <span className="mr-2">
                {platformType === 'vk' && '🔵'}
                {platformType === 'youtube' && '▶️'}
                {platformType === 'dzen' && '📰'}
              </span>
              Подключить {platformType === 'vk' && 'VK'}
                         {platformType === 'youtube' && 'YouTube'}
                         {platformType === 'dzen' && 'Dzen'}
            </h2>

            {platformType === 'vk' && (
              <>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">VK Group ID</label>
                  <input
                    type="text"
                    value={platformForm.group_id || ''}
                    onChange={(e) => setPlatformForm({...platformForm, group_id: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="-123456789 или my_group"
                  />
                  <p className="text-xs text-gray-500 mt-1">ID группы VK (со знаком минус)</p>
                </div>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">Access Token</label>
                  <input
                    type="password"
                    value={platformForm.access_token || ''}
                    onChange={(e) => setPlatformForm({...platformForm, access_token: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="vk1.a..."
                  />
                  <p className="text-xs text-gray-500 mt-1">Токен с правами wall, groups</p>
                </div>
              </>
            )}

            {platformType === 'youtube' && (
              <>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">YouTube Channel ID</label>
                  <input type="text" value={platformForm.channel_id || ''}
                    onChange={(e) => setPlatformForm({...platformForm, channel_id: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="UC..." />
                </div>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">YouTube API Key</label>
                  <input type="password" value={platformForm.api_key || ''}
                    onChange={(e) => setPlatformForm({...platformForm, api_key: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="AIza..." />
                  <p className="text-xs text-gray-500 mt-1">YouTube Data API v3 key</p>
                </div>
              </>
            )}

            {platformType === 'dzen' && (
              <>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">Dzen Channel ID</label>
                  <input type="text" value={platformForm.channel_id || ''}
                    onChange={(e) => setPlatformForm({...platformForm, channel_id: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="123456" />
                </div>
                <div className="mb-4">
                  <label className="block text-gray-400 text-sm mb-2">Dzen API Key</label>
                  <input type="password" value={platformForm.api_key || ''}
                    onChange={(e) => setPlatformForm({...platformForm, api_key: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    placeholder="Dzen API key" />
                </div>
              </>
            )}

            <div className="flex gap-3 mt-6">
              <button onClick={handleConnectPlatform} disabled={connecting}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                {connecting ? 'Подключение...' : 'Подключить'}
              </button>
              <button onClick={() => setShowPlatformModal(false)} disabled={connecting}
                className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50">
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

'''
    
    # Ищем {/* Modal for schedule */} и вставляем ПЕРЕД ним
    if '{/* Modal for schedule */}' in s:
        s = s.replace('{/* Modal for schedule */}', platform_modal + '{/* Modal for schedule */}', 1)
        f.write_text(s, encoding='utf-8')
        print("✅ Модалка showPlatformModal добавлена в JSX")
    else:
        print("❌ Не найдено место для вставки модалки")