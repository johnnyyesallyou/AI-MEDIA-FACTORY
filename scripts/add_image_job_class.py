import pathlib, py_compile

f = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = f.read_text(encoding='utf-8')

if 'class ImageJob' in s:
    print("ℹ️ ImageJob уже существует")
else:
    image_job_class = '''

class ImageJob:
    """
    Sprint 11: Генерирует картинки для approved постов через Pollinations AI.
    Запускается перед PublishJob для добавления визуального контента.
    """

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        logger.info("ImageJob started")

        db = SessionLocal()
        processed = 0
        generated = 0
        failed = 0

        try:
            from core.repositories.content_repository import ContentRepository
            from engines.image.engine import ImageEngine

            repo = ContentRepository(db)

            # Берём approved посты БЕЗ image_url
            items = repo.list_all(status="approved", limit=10)
            items = [i for i in items if not getattr(i, 'image_url', None)]

            logger.info(f"Items without images: {len(items)}")

            if not items:
                logger.info("No items need images")
                return {"status": "ok", "processed": 0, "generated": 0, "failed": 0}

            image_engine = ImageEngine()

            for item in items:
                try:
                    processed += 1

                    # Извлекаем название аниме из headline (в кавычках)
                    import re
                    anime_match = re.search(r'[""«»]([^""«»]+)[""«»]', item.headline)
                    anime_title = anime_match.group(1) if anime_match else item.headline[:50]

                    logger.info(f"Generating image for: {anime_title}...")

                    # Генерируем картинку
                    result = image_engine.generate_anime_poster(
                        anime_title=anime_title,
                        context=item.headline
                    )

                    if result and result.get("image_url") and 'error' not in result:
                        item.image_url = result["image_url"]
                        item.image_prompt = result.get("prompt", "")
                        db.commit()
                        generated += 1
                        logger.info(f"✅ Image generated for {item.id}")
                    else:
                        logger.warning(f"Failed to generate image for {item.id}: {result}")
                        failed += 1

                except Exception as e:
                    logger.exception(f"Image generation failed for {item.id}: {e}")
                    failed += 1
                    db.rollback()

            logger.info(f"ImageJob finished: processed={processed}, generated={generated}, failed={failed}")
            return {
                "status": "ok",
                "processed": processed,
                "generated": generated,
                "failed": failed
            }

        except Exception as e:
            logger.exception(f"ImageJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()

'''
    # Вставляем ImageJob перед последним классом (PublishJob)
    lines = s.split('\n')
    insert_idx = None
    for i, line in enumerate(lines):
        if line.startswith('class PublishJob:'):
            insert_idx = i
            break

    if insert_idx:
        lines.insert(insert_idx, image_job_class)
        s = '\n'.join(lines)
        f.write_text(s, encoding='utf-8')
        print(f"✅ ImageJob добавлен перед PublishJob (строка {insert_idx+1})")
    else:
        # Вставляем в конец
        s += image_job_class
        f.write_text(s, encoding='utf-8')
        print("✅ ImageJob добавлен в конец файла")

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ automation_jobs.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")