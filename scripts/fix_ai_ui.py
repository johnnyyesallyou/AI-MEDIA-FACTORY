import pathlib
p = pathlib.Path('./frontend/src/pages/AIModels.tsx')
s = p.read_text(encoding='utf-8').replace('\r\n', '\n')
changed = []

# Заменяем импорт
if 'aiAPISafe' not in s:
    s = s.replace("import { aiAPI } from '../api/client';", "import { aiAPI, aiAPISafe } from '../api/client';")
    changed.append('import')

# Заменяем вызовы getRouting на getRoutingSafe (в useEffect)
if 'aiAPI.getRouting()' in s and 'aiAPISafe.getRouting()' not in s:
    s = s.replace('aiAPI.getRouting()', 'aiAPISafe.getRouting()')
    changed.append('getRouting')

# Заменяем listModels на безопасную версию
if 'aiAPI.listModels()' in s and 'aiAPISafe.listModels()' not in s:
    s = s.replace('aiAPI.listModels()', 'aiAPISafe.listModels()')
    changed.append('listModels')

# Добавляем состояние для отслеживания mock-режима
if 'isMockMode' not in s:
    s = s.replace('const [loading, setLoading] = useState(true);', 'const [loading, setLoading] = useState(true);\n  const [isMockMode, setIsMockMode] = useState(false);')
    changed.append('state')

# Добавляем баннер mock-режима в return (в начало контейнера)
if 'isMockMode &&' not in s:
    banner = '''      {isMockMode && (
        <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <span className="text-yellow-400 mr-2">⚠️</span>
            <div>
              <div className="text-yellow-200 font-medium">Демонстрационный режим</div>
              <div className="text-yellow-400/80 text-sm">API routing ещё не реализован. Показаны примерные данные. Настройки не сохраняются.</div>
            </div>
          </div>
        </div>
      )}

'''
    # Вставляем после заголовка
    s = s.replace('<h1 className="text-3xl font-bold text-white">AI Models</h1>', '<h1 className="text-3xl font-bold text-white">AI Models</h1>\n' + banner)
    changed.append('banner')

# Обновляем логику загрузки — детектим mock
if 'r._isMock' not in s and 'aiAPISafe.getRouting()' in s:
    # Ищем блок где обрабатывается Promise.all или отдельные запросы
    # Добавляем проверку _isMock
    old_setstate = 'setRouting(routingResponse.data);'
    if old_setstate in s:
        s = s.replace(
            'const routingResponse = await aiAPISafe.getRouting();\n      setRouting(routingResponse.data);',
            'const routingResponse = await aiAPISafe.getRouting();\n      setRouting(routingResponse.data);\n      if ((routingResponse as any)._isMock) setIsMockMode(true);'
        )
        changed.append('mock_detect')

if changed:
    p.write_text(s, encoding='utf-8')
    print(f'OK AIModels.tsx patched: {", ".join(changed)}')
else:
    print('nothing changed')