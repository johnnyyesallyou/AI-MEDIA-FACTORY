import pathlib

p = pathlib.Path("/app/backend/automation/jobs/automation_jobs.py")
c = p.read_text(encoding="utf-8")

# Ищем строку 611: logger.info("✅ Published item=%s...")
# Добавляем создание PostMetric ПОСЛЕ неё

old_pattern = '''                    db.commit()
                    published += 1
                    logger.info("✅ Published item=%s platform=%s message_id=%s", item.id, platform, result.message_id)'''

new_pattern = '''                    db.commit()
                    published += 1
                    logger.info("✅ Published item=%s platform=%s message_id=%s", item.id, platform, result.message_id)
                    
                    # Sprint 50: создаём PostMetric для аналитики
                    try:
                        from core.models.analytics import PostMetric
                        post_metric = PostMetric(
                            post_id=item.id,
                            channel_id=channel.id if channel else None,
                            platform=platform,
                            published_at=result.published_at,
                            text_length=len(full_text),
                            external_id=str(result.message_id) if result.message_id else None,
                        )
                        db.add(post_metric)
                        db.commit()
                        logger.info("✅ PostMetric created for item=%s", item.id)
                    except Exception as metric_e:
                        logger.warning("Failed to create PostMetric for item=%s: %s", item.id, metric_e)'''

if old_pattern in c:
    c = c.replace(old_pattern, new_pattern, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] PostMetric creation added to PublishJob")
else:
    print("[!] Pattern not found")