-- Sprint 8.2 Seed Data: Templates, Profiles, Workflows

-- ============================================
-- 1. WORKFLOWS (если нет — создаём)
-- ============================================

INSERT INTO workflows (id, name, description, definition, is_active)
VALUES 
  ('wf-default-full', 'Default Full', 'Полный цикл: research → decision → writing → evaluation → revision → re_evaluation → publish',
   '{"stages": ["research", "decision", "writing", "evaluation", "revision", "re_evaluation", "publish"]}'::json, true),
  ('wf-simple', 'Simple', 'Упрощённый: research → writing → evaluation → publish',
   '{"stages": ["research", "writing", "evaluation", "publish"]}'::json, true),
  ('wf-research-only', 'Research Only', 'Только сбор тем (без публикации)',
   '{"stages": ["research"]}'::json, true)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 2. CHANNEL PROFILES (стиль подачи)
-- ============================================

INSERT INTO channel_profiles (id, name, description, platform, audience, tone, format, emoji_usage, length_chars, call_to_action, forbidden_words, example)
VALUES
  ('prof-telegram-expert', 'Telegram Эксперт', 'Профессиональный стиль для IT-аудитории Telegram',
   'telegram', 'AI-разработчики, фаундеры, технические специалисты',
   'Экспертный, с лёгкой иронией, без воды. Как опытный инженер делится инсайтами.',
   'Цепляющий заголовок + 2-3 абзаца сути + вопрос к аудитории',
   'Умеренное (1-2 эмодзи для акцентов)',
   900, 'Что думаете? Поделитесь мнением.',
   '["кликбейт", "шок", "сенсация", "невероятно", "вы не поверите"]'::json,
   'Google представила квантовый чип Willow' || E'\n\n' || 'Пока все обсуждали GPT-5, Google тихо совершила революцию.'),

  ('prof-telegram-simple', 'Telegram Простой', 'Понятный стиль для широкой аудитории',
   'telegram', 'Широкая аудитория, интересующаяся технологиями',
   'Простой, понятный, без технического жаргона',
   'Заголовок + 1-2 абзаца сути + почему это важно для обычного человека',
   'Минимальное (1 эмодзи в заголовке)',
   600, 'Как вам такое?',
   '["алгоритм", "нейросеть", "квантовый", "API", "фреймворк"]'::json,
   'Google создала компьютер будущего' || E'\n\n' || 'Представьте задачу, которую обычный компьютер будет решать миллион лет.'),

  ('prof-vk-expert', 'VK Эксперт', 'Развёрнутый профессиональный стиль для ВКонтакте',
   'vk', 'IT-специалисты ВКонтакте',
   'Профессиональный, более развёрнутый чем в Telegram',
   'Заголовок + введение + 3-5 пунктов + вывод + хэштеги',
   'Умеренное (2-5 эмодзи для структурирования)',
   1500, 'Подписывайтесь на обновления!',
   '["кликбейт", "шок", "сенсация"]'::json,
   '5 трендов AI в 2024 году' || E'\n\n' || '1. Мультимодальные модели...'),

  ('prof-dzen-expert', 'Дзен Эксперт', 'Познавательный сторителлинг для Дзен',
   'dzen', 'Широкая аудитория Дзен',
   'Познавательный, с элементами сторителлинга',
   'Цепляющий заголовок + введение + 5-10 абзацев + заключение',
   'Минимальное (1-3 эмодзи)',
   3000, 'Подписывайтесь на канал!',
   '["кликбейт", "шок", "сенсация", "невероятно"]'::json,
   'Как квантовые компьютеры изменят нашу жизнь' || E'\n\n' || 'Представьте мир, где...'),

  ('prof-youtube-expert', 'YouTube Эксперт', 'Энергичный разговорный стиль для YouTube',
   'youtube', 'Зрители YouTube о технологиях',
   'Энергичный, разговорный, с призывами к действию',
   'Hook + суть + призыв подписаться',
   'Активное (3-8 эмодзи)',
   800, 'Подписывайтесь и ставьте лайк!',
   '["скучный", "монотонный"]'::json,
   '🔥 НОВЫЙ КВАНТОВЫЙ ЧИП! 🚀')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 3. CHANNEL TEMPLATES (ЧТО делать)
-- ============================================

INSERT INTO channel_templates (id, name, description, category, language_search, language_publish, timezone, sources, workflow_id, model, temperature, cron_expression, max_posts_per_day, minimum_quality_score, auto_publish, human_review)
VALUES
  ('tpl-ai-news-ru', 'Новости AI (RU)', 'Ежедневные новости ИИ-индустрии на русском',
   'technology/ai', 'ru', 'ru', 'Europe/Moscow',
   '[{"id": "habr-ai", "name": "Habr AI", "source_type": "rss", "url": "https://habr.com/ru/rss/hub/artificial_intelligence/", "priority": 5}, {"id": "vc-ai", "name": "VC AI", "source_type": "rss", "url": "https://vc.ru/rss/ai", "priority": 4}]'::json,
   'wf-default-full', 'llama3.1:8b', '0.7', '0 */2 * * *', 10, 70, true, false),

  ('tpl-business-analytics', 'Бизнес Аналитика', 'Аналитика для бизнес-аудитории',
   'business/analytics', 'en', 'ru', 'Europe/Moscow',
   '[{"id": "techcrunch", "name": "TechCrunch", "source_type": "rss", "url": "https://techcrunch.com/feed/", "priority": 5}, {"id": "forbes-tech", "name": "Forbes Tech", "source_type": "rss", "url": "https://www.forbes.com/innovation/feed/", "priority": 4}]'::json,
   'wf-simple', 'mistral-nemo:12b', '0.7', '0 */4 * * *', 5, 80, false, true),

  ('tpl-gaming-news', 'Игровые Новости', 'Новости игровой индустрии',
   'gaming/news', 'ru', 'ru', 'Europe/Moscow',
   '[{"id": "igdb", "name": "IGN Russia", "source_type": "rss", "url": "https://ru.ign.com/feed", "priority": 5}]'::json,
   'wf-simple', 'llama3.1:8b', '0.8', '0 */1 * * *', 20, 65, true, false),

  ('tpl-crypto-trading', 'Крипто Трейдинг', 'Новости и анализ крипторынка',
   'finance/crypto', 'en', 'ru', 'Europe/Moscow',
   '[{"id": "coindesk", "name": "CoinDesk", "source_type": "rss", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "priority": 5}]'::json,
   'wf-default-full', 'mistral-nemo:12b', '0.6', '0 */3 * * *', 8, 75, false, true)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 4. Проверка
-- ============================================
SELECT 'workflows' as type, COUNT(*) as count FROM workflows
UNION ALL
SELECT 'profiles', COUNT(*) FROM channel_profiles
UNION ALL
SELECT 'templates', COUNT(*) FROM channel_templates;