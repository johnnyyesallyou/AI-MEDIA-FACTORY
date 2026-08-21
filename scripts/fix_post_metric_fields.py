import pathlib

p = pathlib.Path("/app/backend/automation/jobs/automation_jobs.py")
c = p.read_text(encoding="utf-8")

# Заменяем неправильные поля на правильные
old_pattern = '''                    # Sprint 50: создаём PostMetric для аналитики
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

new_pattern = '''                    # Sprint 50: создаём PostMetric для аналитики
                    try:
                        from core.models.analytics import PostMetric
                        post_metric = PostMetric()
                        post_metric.content_id = item.id
                        post_metric.channel_id = channel.id if channel else None
                        post_metric.platform = platform
                        post_metric.published_at = result.published_at
                        post_metric.external_id = str(result.message_id) if result.message_id else None
                        db.add(post_metric)
                        db.commit()
                        logger.info("✅ PostMetric created for item=%s", item.id)
                    except Exception as metric_e:
                        logger.warning("Failed to create PostMetric for item=%s: %s", item.id, metric_e)'''

if old_pattern in c:
    c = c.replace(old_pattern, new_pattern, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] PostMetric creation fixed with correct fields")
else:
    print("[!] Pattern not found")