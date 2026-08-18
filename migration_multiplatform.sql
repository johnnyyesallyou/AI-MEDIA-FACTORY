-- Sprint 11: Multi-Platform Publishers
-- Добавляем колонки для VK, YouTube, Dzen

-- VK
ALTER TABLE channels ADD COLUMN IF NOT EXISTS vk_group_id VARCHAR(50);
ALTER TABLE channels ADD COLUMN IF NOT EXISTS vk_access_token VARCHAR(255);

-- YouTube
ALTER TABLE channels ADD COLUMN IF NOT EXISTS youtube_channel_id VARCHAR(100);
ALTER TABLE channels ADD COLUMN IF NOT EXISTS youtube_api_key VARCHAR(255);
ALTER TABLE channels ADD COLUMN IF NOT EXISTS youtube_access_token TEXT;
ALTER TABLE channels ADD COLUMN IF NOT EXISTS youtube_refresh_token TEXT;

-- Dzen
ALTER TABLE channels ADD COLUMN IF NOT EXISTS dzen_channel_id VARCHAR(100);
ALTER TABLE channels ADD COLUMN IF NOT EXISTS dzen_api_key VARCHAR(255);

-- Обновляем timestamps
UPDATE channels SET updated_at = NOW() WHERE updated_at IS NULL;