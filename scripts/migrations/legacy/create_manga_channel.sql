-- Create manga channel directly via SQL (avoid SQLAlchemy FK issues)

INSERT INTO channels (
    id, name, platform, language_search, language_publish,
    style_profile, timezone, is_connected, is_active, sources,
    image_profile, created_at, updated_at
)
SELECT 
    'manga-channel-001',
    'Манга — новые главы',
    'telegram',
    'ru',
    'ru',
    'manga',
    'UTC',
    false,
    true,
    '[]'::json,
    '{"mode": "source_first", "source_image": true, "search_image": true, "ai_generation": "fallback", "require_relevance": true, "style": "manga"}'::json,
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM channels WHERE name = 'Манга — новые главы'
);

SELECT name, platform, style_profile, image_profile->>'mode' as mode, is_active
FROM channels WHERE name = 'Манга — новые главы';
