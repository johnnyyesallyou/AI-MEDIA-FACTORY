import pathlib, py_compile

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
lines = p.read_text(encoding='utf-8').split('\n')

# 1. Находим начало класса PublishJob (строка 369 = "class PublishJob:")
class_start = None
for i, line in enumerate(lines):
    if line.strip() == 'class PublishJob:':
        class_start = i
        break

if class_start is None:
    print("❌ class PublishJob не найден")
    exit(1)

print(f"Класс PublishJob начинается на строке {class_start + 1}")

# 2. Удаляем ВСЁ от class_start до конца файла
lines = lines[:class_start]

# 3. Вставляем чистый класс PublishJob
clean_class = '''class PublishJob:

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("publish")

        logger.info("PublishJob started")

        db = SessionLocal()

        # === RATE LIMITS & AUTO_PUBLISH ===
        schedule = None
        if channel:
            schedule = db.query(ChannelScheduleORM).filter(
                ChannelScheduleORM.channel_id == channel.id
            ).first()

        auto_publish = schedule.auto_publish if schedule else True
        max_posts_per_day = schedule.max_posts_per_day if schedule else 3

        if not auto_publish:
            logger.info("Auto-publish disabled for channel %s", channel.id if channel else None)
            p_logger.finish("success", details="Auto-publish disabled for this channel")
            db.close()
            return {"status": "skipped", "reason": "auto_publish_disabled", "published": 0, "failed": 0}

        # Лимит публикаций за сутки
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        published_today = 0
        if channel:
            published_today = db.query(ContentORM).filter(
                ContentORM.channel_id == channel.id,
                ContentORM.status == "published",
                ContentORM.published_at >= today_start
            ).count()

        remaining = max(0, max_posts_per_day - published_today)
        logger.info(
            "Rate limit check: channel=%s published_today=%s max=%s remaining=%s",
            channel.id if channel else None, published_today, max_posts_per_day, remaining
        )

        if remaining <= 0:
            logger.info("Rate limit reached for channel %s", channel.id if channel else None)
            p_logger.finish(
                "success",
                details=f"Rate limit reached ({published_today}/{max_posts_per_day} posts today)"
            )
            db.close()
            return {
                "status": "skipped",
                "reason": "rate_limit",
                "published_today": published_today,
                "max_posts_per_day": max_posts_per_day,
                "published": 0,
                "failed": 0,
            }

        published = 0
        failed = 0

        try:
            from core.repositories.channel_repository import ChannelRepository
            from backend.automation.publishers import PublisherFactory

            content_repo = ContentRepository(db)
            channel_repo = ChannelRepository(db)

            # Получаем одобренные посты для публикации
            items = content_repo.list_all(
                status="approved",
                limit=min(10, remaining)
            )
            logger.info("Publish queue size=%s", len(items))

            # Sprint 8.5: получаем publisher для платформы канала
            platform = getattr(channel, "platform", "telegram") or "telegram"
            publisher = PublisherFactory.get(platform)
            logger.info("Using publisher for platform=%s", platform)

            for item in items:
                try:
                    # Проверяем что канал имеет credentials
                    if (
                        not channel
                        or not getattr(channel, "is_connected", False)
                    ):
                        logger.warning(
                            "Skip publish item=%s channel not connected",
                            item.id
                        )
                        continue

                    # Собираем credentials для платформы
                    credentials = {
                        "bot_token": getattr(channel, "bot_token", None),
                        "chat_id": getattr(channel, "chat_id", None),
                    }

                    if not publisher.validate_credentials(credentials):
                        logger.warning(
                            "Skip publish item=%s invalid credentials for platform=%s",
                            item.id, platform
                        )
                        continue

                    # Публикуем через PublisherFactory
                    result = publisher.publish(
                        text=item.draft_text,
                        credentials=credentials,
                        channel=channel
                    )

                    if not result.success:
                        logger.warning(
                            "Skip publish item=%s platform=%s error=%s",
                            item.id, platform, result.error
                        )
                        failed += 1
                        item.publish_error = result.error
                        db.commit()
                        continue

                    # Успешная публикация
                    item.status = "published"
                    item.telegram_message_id = str(result.message_id) if result.message_id else None
                    item.published_at = result.published_at
                    item.publish_error = None

                    db.commit()

                    published += 1

                    logger.info(
                        "Published item=%s message=%s platform=%s",
                        item.id,
                        result.message_id,
                        platform
                    )

                except Exception as e:
                    db.rollback()
                    failed += 1
                    item.publish_error = str(e)
                    db.commit()
                    logger.exception(
                        "Publish failed item=%s",
                        item.id
                    )

            p_logger.finish("success", details=f"Published {published}, failed {failed}")

        except Exception as e:
            logger.exception("PublishJob failed: %s", str(e))
            p_logger.finish("failed", error_message=str(e))
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()

        return {
            "status": "ok",
            "published": published,
            "failed": failed
        }
'''

lines.append(clean_class)

p.write_text('\n'.join(lines), encoding='utf-8')
print("✅ Класс PublishJob заменён на чистую версию")

# 4. Проверяем синтаксис
print("\n🧪 Проверяем синтаксис...")
try:
    py_compile.compile(str(p), doraise=True)
    print("✅✅✅ СИНТАКСИС ВАЛИДЕН! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")