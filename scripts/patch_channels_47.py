import pathlib, re

# ---------- client.ts ----------
p = pathlib.Path("frontend/src/api/client.ts")
c = p.read_text(encoding="utf-8")

if "getTemplates" not in c:
    old = "  get: (id: string) => apiClient.get(`/channels/${id}`),"
    new = old + """
  getTemplates: () => apiClient.get('/channels/templates'),
  createFromTemplate: (templateId: string) => apiClient.post(`/channels/from-template?template_id=${templateId}`),"""
    if old in c:
        c = c.replace(old, new, 1)
        p.write_text(c, encoding="utf-8")
        print("[OK] client.ts: getTemplates + createFromTemplate added")
    else:
        print("[!] client.ts: anchor not found")
else:
    print("[i] client.ts: already has templates API")

# ---------- Channels.tsx ----------
p = pathlib.Path("frontend/src/pages/Channels.tsx")
c = p.read_text(encoding="utf-8")

# 1. Фикс битого import
c = c.replace(
    "import { channelsAPI, automationAPI } from '../api/client, getTemplates, createFromTemplate';",
    "import { channelsAPI, automationAPI } from '../api/client';",
    1,
)

# 2. showTemplateModal -> templateCreating (unused state -> useful state)
c = c.replace(
    "const [showTemplateModal, setShowTemplateModal] = useState(false);",
    "const [templateCreating, setTemplateCreating] = useState<string | null>(null);",
    1,
)

# 3. Удаляем старые функции прошлого патча (loadTemplates/createChannelFromTemplate)
c = re.sub(
    r"\n  const loadTemplates = async \(\) => \{[\s\S]*?\n  \}\n(?:\n  const createChannelFromTemplate[\s\S]*?\n  \}\n)?",
    "\n",
    c,
    count=1,
)

# 4. Расширяем модалку создания (до вставки блока)
c = c.replace(
    '<div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">\n            <h2 className="text-2xl font-bold text-white mb-6">Создать канал</h2>',
    '<div className="bg-gray-800 rounded-lg p-6 w-full max-w-lg border border-gray-700">\n            <h2 className="text-2xl font-bold text-white mb-6">Создать канал</h2>',
    1,
)

# 5. Новые обработчики перед handleCreateChannel
handler = '''  const loadTemplates = async () => {
    if (templates.length > 0) return;
    try {
      const r = await channelsAPI.getTemplates();
      setTemplates(r.data);
    } catch (e) {
      console.error('Failed to load templates:', e);
    }
  };

  const handleCreateFromTemplate = async (templateId: string) => {
    setTemplateCreating(templateId);
    try {
      await channelsAPI.createFromTemplate(templateId);
      setShowCreateModal(false);
      await loadChannels();
    } catch (e) {
      console.error('Failed to create from template:', e);
    } finally {
      setTemplateCreating(null);
    }
  };

  const handleCreateChannel = async () => {'''
c = c.replace("  const handleCreateChannel = async () => {", handler, 1)

# 6. Кнопки "Новый канал"/"Создать канал" открывают модалку + грузят шаблоны
c = c.replace(
    "onClick={() => setShowCreateModal(true)}",
    "onClick={() => { setShowCreateModal(true); loadTemplates(); }}",
)

# 7. Блок шаблонов ВНУТРИ существующей модалки (после заголовка)
old_h2 = '<h2 className="text-2xl font-bold text-white mb-6">Создать канал</h2>'
block = old_h2 + '''

            {/* Sprint 47: быстрый старт из шаблона (улучшение существующей модалки) */}
            <div className="mb-6">
              <div className="text-sm text-gray-400 mb-2">Быстрый старт из шаблона:</div>
              <div className="grid grid-cols-3 gap-2">
                {templates.map((t: any) => (
                  <button
                    key={t.id}
                    onClick={() => handleCreateFromTemplate(t.id)}
                    disabled={templateCreating !== null}
                    className="p-3 bg-gray-700/50 border border-gray-600 rounded-lg hover:border-blue-500 hover:bg-gray-700 transition-colors text-left disabled:opacity-50"
                  >
                    <div className="text-lg mb-1">{t.id === 'news' ? '📰' : t.id === 'anime' ? '🍥' : '📚'}</div>
                    <div className="text-white text-sm font-medium">
                      {t.id === 'news' ? 'Новости' : t.id === 'anime' ? 'Аниме' : 'Манга'}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {templateCreating === t.id ? 'Создание…' : '1 клик'}
                    </div>
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-2 mt-4">
                <div className="flex-1 h-px bg-gray-700"></div>
                <span className="text-xs text-gray-500">или вручную</span>
                <div className="flex-1 h-px bg-gray-700"></div>
              </div>
            </div>'''
c = c.replace(old_h2, block, 1)

p.write_text(c, encoding="utf-8")
print("[OK] Channels.tsx: одна улучшенная модалка (templates + manual)")