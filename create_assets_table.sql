-- Sprint 11: Image Domain - таблица assets
CREATE TABLE IF NOT EXISTS assets (
    id VARCHAR PRIMARY KEY,
    content_id VARCHAR NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    type VARCHAR NOT NULL DEFAULT 'image',  -- image/video/audio
    storage_path VARCHAR NOT NULL,          -- assets/2026/07/uuid.png
    public_url VARCHAR,                     -- http://localhost:8000/assets/uuid.png
    prompt TEXT,                            -- промпт для генерации
    model VARCHAR,                          -- flux/sdxl/comfyui
    seed INTEGER,                           -- seed для воспроизводимости
    width INTEGER,
    height INTEGER,
    generation_time_ms INTEGER,
    status VARCHAR DEFAULT 'generated',     -- generating/generated/failed
    metadata JSONB,                         -- доп. данные (quality_score, etc)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_assets_content_id ON assets(content_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);

-- Обновляем content таблицу для связи с assets
ALTER TABLE content ADD COLUMN IF NOT EXISTS asset_id VARCHAR REFERENCES assets(id);
ALTER TABLE content ADD COLUMN IF NOT EXISTS image_prompt TEXT;