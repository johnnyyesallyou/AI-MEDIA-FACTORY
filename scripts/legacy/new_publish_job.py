class PublishJob:
    """
    Sprint 11 (refactored): Публикует уже готовые approved посты.
    
    ВАЖНО: НЕ генерирует текст заново — использует существующий draft_text.
    Текст уже прошёл WritingJob + EvaluatorJob + получил approval.
    """

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("publish")

        logger.info("PublishJob started (refactored: using existing draft_text)")

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

            # Sprint 11: получаем publisher для платформы канала
            platform = getattr(channel, "platform", "telegram") or "telegram"
            publisher = PublisherFactory.get(platform)
            logger.info("Using publisher for platform=%s", platform)

            for item in items:
                try:
                    # Проверяем что канал подключен
                    if not channel or not getattr(channel, "is_connected", False):
                        logger.warning("Skip publish item=%s channel not connected", item.id)
                        continue

                    # Проверяем что есть готовый draft_text (не генерируем заново!)
                    if not item.draft_text or len(item.draft_text.strip()) < 50:
                        logger.warning("Skip publish item=%s no draft_text or too short", item.id)
                        item.status = "needs_revision"
                        item.last_revision_reason = "No valid draft_text for publishing"
                        db.commit()
                        failed += 1
                        continue

                    # Собираем credentials в зависимости от платформы
                    if platform == "vk":
                        credentials = {
                            "group_id": getattr(channel, "vk_group_id", None),
                            "access_token": getattr(channel, "vk_access_token", None),
                        }
                    elif platform == "youtube":
                        credentials = {
                            "channel_id": getattr(channel, "youtube_channel_id", None),
                            "api_key": getattr(channel, "youtube_api_key", None),
                        }
                    elif platform == "dzen":
                        credentials = {
                            "channel_id": getattr(channel, "dzen_channel_id", None),
                            "api_key": getattr(channel, "dzen_api_key", None),
                        }
                    else:  # telegram (default)
                        credentials = {
                            "bot_token": getattr(channel, "bot_token", None),
                            "chat_id": getattr(channel, "chat_id", None),
                        }

                    if not publisher.validate_credentials(credentials):
                        logger.warning("Skip publish item=%s invalid credentials for platform=%s", item.id, platform)
                        continue

                    # Публикуем через PublisherFactory (используем существующий draft_text!)
                    full_text = f"{item.headline}\n\n{item.draft_text}"
                    result = publisher.publish(
                        text=full_text,
                        credentials=credentials,
                        channel=channel
                    )

                    if not result.success:
                        logger.warning("Skip publish item=%s platform=%s error=%s", item.id, platform, result.error)
                        failed += 1
                        item.publish_error = result.error
                        db.commit()
                        continue

                    # Успешная публикация
                    item.status = "published"
                    item.telegram_message_id = str(result.message_id) if result.message_id else None
                    item.published_at = result.published_at
                    item.publish_error = None

                    # Sprint 11: сохраняем platform-specific данные если поле есть
                    if hasattr(item, "publish_platform_data") and result.platform_data:
                        item.publish_platform_data = result.platform_data

                    db.commit()
                    published += 1
                    logger.info("✅ Published item=%s platform=%s message_id=%s", item.id, platform, result.message_id)

                except Exception as e:
                    db.rollback()
                    logger.exception("Publish failed for item=%s error=%s", item.id, e)
                    failed += 1

            p_logger.finish("success", details=f"Published {published}, failed {failed}")
            return {"status": "ok", "published": published, "failed": failed}

        except Exception as e:
            error_msg = str(e)
            logger.exception("PublishJob failed with error: %s", error_msg)
            p_logger.finish("failed", error_message=error_msg)
            return {"status": "failed", "error": error_msg}
        finally:
            db.close()