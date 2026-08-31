SET client_encoding = 'UTF8';

UPDATE workflows SET description = 'Простой пайплайн: research → writing → evaluation → publish' WHERE id = 'wf-simple';

UPDATE workflows SET description = 'Полный цикл с доработкой: research → decision → writing → evaluation → revision → re_evaluation → publish' WHERE id = 'wf-default-full';

UPDATE workflows SET description = 'Только сбор тем из RSS (без генерации и публикации)' WHERE id = 'wf-research-only';

UPDATE workflows SET description = 'Legacy: research → decision → writing → fact check → image → review → telegram' WHERE id = '35ab8d8e-6e1c-49a1-826f-165e99e4fb5c';

UPDATE workflows SET created_at = NOW(), updated_at = NOW() WHERE created_at IS NULL;