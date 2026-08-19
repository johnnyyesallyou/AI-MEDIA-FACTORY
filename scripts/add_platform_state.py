import pathlib

f = pathlib.Path('./frontend/src/pages/Channels.tsx')
s = f.read_text(encoding='utf-8')

# 1. Добавляем state для platform модалки (после telegramForm)
if 'showPlatformModal' not in s:
    platform_state = '''
  // Sprint 11: Universal platform connection modal (VK/YouTube/Dzen)
  const [showPlatformModal, setShowPlatformModal] = useState(false);
  const [platformType, setPlatformType] = useState<string>('vk');
  const [platformForm, setPlatformForm] = useState<Record<string, string>>({});
'''
    # Вставляем после telegramForm state
    s = s.replace(
        '    chat_id: \'\'\n  });',
        '    chat_id: \'\'\n  });' + platform_state,
        1
    )
    print("✅ Добавлены state: showPlatformModal, platformType, platformForm")

# 2. Добавляем функции openVkModal, openYoutubeModal, openDzenModal (после openTelegramModal)
if 'openVkModal' not in s:
    platform_functions = '''
  const openVkModal = (channelId: string) => {
    setSelectedChannelId(channelId);
    const channel = channels.find(c => c.id === channelId);
    setPlatformType('vk');
    setPlatformForm({
      group_id: channel?.vk_group_id || '',
      access_token: channel?.vk_access_token || ''
    });
    setShowPlatformModal(true);
  };

  const openYoutubeModal = (channelId: string) => {
    setSelectedChannelId(channelId);
    const channel = channels.find(c => c.id === channelId);
    setPlatformType('youtube');
    setPlatformForm({
      channel_id: channel?.youtube_channel_id || '',
      api_key: channel?.youtube_api_key || ''
    });
    setShowPlatformModal(true);
  };

  const openDzenModal = (channelId: string) => {
    setSelectedChannelId(channelId);
    const channel = channels.find(c => c.id === channelId);
    setPlatformType('dzen');
    setPlatformForm({
      channel_id: channel?.dzen_channel_id || '',
      api_key: channel?.dzen_api_key || ''
    });
    setShowPlatformModal(true);
  };

  const handleConnectPlatform = async () => {
    if (!selectedChannelId) return;
    setConnecting(true);
    try {
      if (platformType === 'vk') {
        await channelsAPI.connectVk(selectedChannelId, platformForm);
        alert('✅ VK группа успешно подключена!');
      } else if (platformType === 'youtube') {
        await channelsAPI.connectYoutube(selectedChannelId, platformForm);
        alert('✅ YouTube канал успешно подключен!');
      } else if (platformType === 'dzen') {
        await channelsAPI.connectDzen(selectedChannelId, platformForm);
        alert('✅ Дзен канал успешно подключен!');
      }
      setShowPlatformModal(false);
      loadChannels();
    } catch (error) {
      console.error(`Error connecting ${platformType}:`, error);
      alert(`❌ Ошибка подключения: ${(error as Error).message}`);
    } finally {
      setConnecting(false);
    }
  };
'''
    # Вставляем после openTelegramModal функции
    s = s.replace(
        '    setShowTelegramModal(true);\n  };',
        '    setShowTelegramModal(true);\n  };' + platform_functions,
        1
    )
    print("✅ Добавлены функции: openVkModal, openYoutubeModal, openDzenModal, handleConnectPlatform")

f.write_text(s, encoding='utf-8')