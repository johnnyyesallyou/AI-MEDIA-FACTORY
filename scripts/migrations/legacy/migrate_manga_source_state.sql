-- Sprint 15: Create manga_source_states table

CREATE TABLE IF NOT EXISTS manga_source_states (
    id VARCHAR PRIMARY KEY,
    source VARCHAR NOT NULL,
    title_id VARCHAR NOT NULL,
    title_name VARCHAR(255) NOT NULL,
    title_name_en VARCHAR(255),
    title_slug VARCHAR(255),
    title_url VARCHAR(500),
    cover_url VARCHAR(500),
    last_chapter_number VARCHAR(50),
    last_chapter_id VARCHAR(100),
    last_chapter_url VARCHAR(500),
    last_seen_at TIMESTAMP DEFAULT NOW(),
    first_seen_at TIMESTAMP DEFAULT NOW(),
    total_chapters_seen INTEGER DEFAULT 1,
    extra_data JSONB,
    CONSTRAINT uq_manga_source_state_source_title UNIQUE (source, title_id)
);

CREATE INDEX IF NOT EXISTS ix_manga_source_states_source ON manga_source_states(source);
CREATE INDEX IF NOT EXISTS ix_manga_source_states_title_id ON manga_source_states(title_id);

SELECT COUNT(*) as total FROM manga_source_states;
