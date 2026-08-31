-- Sprint 11: Добавляем поля для картинок в content
ALTER TABLE content ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);
ALTER TABLE content ADD COLUMN IF NOT EXISTS image_prompt TEXT;