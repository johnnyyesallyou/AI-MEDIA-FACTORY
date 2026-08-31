-- Sprint 14: Set image_profile for active channels

BEGIN;

UPDATE channels 
SET image_profile = '{"mode": "source_first", "source_image": true, "search_image": true, "ai_generation": "fallback", "require_relevance": true, "prefer_official": false, "style": "news"}'::json
WHERE name = 'АИ Новости' AND is_active = true;

UPDATE channels 
SET image_profile = '{"mode": "source_first", "source_image": true, "search_image": true, "ai_generation": "fallback", "require_relevance": true, "prefer_official": true, "style": "anime"}'::json
WHERE name = 'AI Anime News' AND is_active = true;

UPDATE channels 
SET image_profile = '{"mode": "source_first", "source_image": true, "search_image": true, "ai_generation": "fallback", "require_relevance": true, "prefer_official": false, "style": "anime"}'::json
WHERE name = 'Test VK Channel' AND is_active = true;

COMMIT;

SELECT name, 
       image_profile->>'mode' as mode, 
       image_profile->>'ai_generation' as ai_gen, 
       image_profile->>'style' as style 
FROM channels 
WHERE is_active = true;
