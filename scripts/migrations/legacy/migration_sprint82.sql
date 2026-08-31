-- Sprint 8.2: Channel Templates & Profiles

-- Таблица шаблонов (ЧТО делать)
CREATE TABLE IF NOT EXISTS channel_templates (
    id VARCHAR PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR,
    category VARCHAR,
    language_search VARCHAR DEFAULT 'en',
    language_publish VARCHAR DEFAULT 'ru',
    timezone VARCHAR DEFAULT 'Europe/Moscow',
    sources JSON DEFAULT '[]',
    workflow_id VARCHAR REFERENCES workflows(id),
    model VARCHAR DEFAULT 'llama3.1:8b',
    temperature VARCHAR DEFAULT '0.7',
    cron_expression VARCHAR DEFAULT '0 */2 * * *',
    max_posts_per_day INTEGER DEFAULT 10,
    minimum_quality_score INTEGER DEFAULT 70,
    auto_publish BOOLEAN DEFAULT true,
    human_review BOOLEAN DEFAULT false,
    retry_policy JSON DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица профилей (КАК подавать)
CREATE TABLE IF NOT EXISTS channel_profiles (
    id VARCHAR PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR,
    platform VARCHAR DEFAULT 'telegram',
    audience VARCHAR,
    tone VARCHAR,
    format VARCHAR,
    emoji_usage VARCHAR,
    length_chars INTEGER DEFAULT 900,
    call_to_action VARCHAR,
    forbidden_words JSON DEFAULT '[]',
    example VARCHAR,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Добавляем FK в channels
ALTER TABLE channels ADD COLUMN IF NOT EXISTS template_id VARCHAR REFERENCES channel_templates(id);
ALTER TABLE channels ADD COLUMN IF NOT EXISTS profile_id VARCHAR REFERENCES channel_profiles(id);

-- Индексы
CREATE INDEX IF NOT EXISTS ix_channels_template_id ON channels(template_id);
CREATE INDEX IF NOT EXISTS ix_channels_profile_id ON channels(profile_id);
CREATE INDEX IF NOT EXISTS ix_channel_templates_workflow_id ON channel_templates(workflow_id);

-- Проверяем
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name IN ('channel_templates', 'channel_profiles');