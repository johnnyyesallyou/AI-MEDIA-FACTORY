-- Sprint 15: Connect Telegram bot to manga channel

UPDATE channels
SET bot_token = 'TELEGRAM_BOT_TOKEN_REDACTED',
    chat_id = '@manga_new_chapters',
    is_connected = true,
    updated_at = NOW()
WHERE name = 'Манга — новые главы';

SELECT name, platform, chat_id, is_connected, is_active
FROM channels WHERE name = 'Манга — новые главы';
