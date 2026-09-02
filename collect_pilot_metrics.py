"""Sprint 69.13: Automated Pilot Metrics Collector (DB-based).

Собирает метрики напрямую из БД, НЕ требует docker.
Запускается каждые 6 часов автоматически.
"""
import sys
import uuid
import json
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, "/app")

from sqlalchemy import text
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM


def collect_metrics_for_channel(db, channel: ChannelORM, cutoff: datetime) -> dict:
    """Собирает метрики для одного канала напрямую из БД."""
    cid = channel.id
    
    # Считаем posts за период
    posts_stats = db.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'published') as published,
            COUNT(*) FILTER (WHERE status = 'failed' OR status = 'error') as failed,
            COUNT(*) FILTER (WHERE status = 'draft') as draft,
            AVG(LENGTH(COALESCE(draft_text, ''))) as avg_len
        FROM content
        WHERE channel_id = :cid AND created_at >= :cutoff
    """), {"cid": cid, "cutoff": cutoff}).fetchone()
    
    total = posts_stats[0] or 0
    published = posts_stats[1] or 0
    failed = posts_stats[2] or 0
    draft = posts_stats[3] or 0
    avg_len = posts_stats[4] or 0
    
    # Topics extracted = topics которые прошли через dedup (новые URL)
    new_topics = db.execute(text("""
        SELECT COUNT(*) FROM content
        WHERE channel_id = :cid 
          AND created_at >= :cutoff
          AND source_url IS NOT NULL 
          AND source_url != ''
    """), {"cid": cid, "cutoff": cutoff}).scalar() or 0
    
    # Duplicated topics: считаем как разницу (topics_extracted - new_topics)
    # Это аппроксимация, так как dedup не сохраняет данные отдельно
    
    # Pipeline runs: кластеризуем posts по времени создания (gap > 5 мин = новый run)
    pipeline_runs_data = db.execute(text("""
        SELECT created_at FROM content
        WHERE channel_id = :cid AND created_at >= :cutoff
        ORDER BY created_at ASC
    """), {"cid": cid, "cutoff": cutoff}).fetchall()
    
    pipeline_runs = 0
    if pipeline_runs_data:
        pipeline_runs = 1
        prev_time = pipeline_runs_data[0][0]
        for row in pipeline_runs_data[1:]:
            curr_time = row[0]
            if (curr_time - prev_time).total_seconds() > 300:  # > 5 min gap
                pipeline_runs += 1
            prev_time = curr_time
    
    # Success rates
    pipeline_successes = pipeline_runs  # Аппроксимация: все runs считаются успешными если есть posts
    pipeline_success_rate = 100.0 if pipeline_runs > 0 else 0.0
    
    publish_success_rate = (published / total * 100) if total > 0 else 0.0
    
    # Sources count
    sources = channel.content_profile.get("sources", []) if channel.content_profile else []
    active_sources = len(sources)
    
    # LLM calls = total posts (каждый post = 1 LLM call)
    total_llm_calls = total
    
    # Average pipeline duration (аппроксимация)
    avg_pipeline_duration = (total_llm_calls * 40.0 / pipeline_runs) if pipeline_runs > 0 else 0
    
    return {
        "pipeline_runs": pipeline_runs,
        "pipeline_successes": pipeline_successes,
        "pipeline_failures": 0,  # TODO: добавить в будущем
        "pipeline_success_rate": pipeline_success_rate,
        "topics_extracted": new_topics,  # Аппроксимация
        "topics_new": new_topics,
        "topics_duplicated": 0,  # TODO: из логов
        "posts_generated": total,
        "posts_published": published,
        "posts_failed": failed,
        "publish_success_rate": publish_success_rate,
        "avg_pipeline_duration_seconds": avg_pipeline_duration,
        "avg_llm_generation_time": 40.0,  # Средняя из Sprint 69.12
        "total_llm_calls": total_llm_calls,
        "error_count": failed,
        "error_types": json.dumps([]),
        "active_sources": active_sources,
        "avg_text_length": avg_len,
    }


def save_metrics_to_db(db, channel: ChannelORM, metrics: dict, hours: int):
    """Сохраняет метрики в таблицу pilot_metrics."""
    metric_id = str(uuid.uuid4())
    
    db.execute(text("""
        INSERT INTO pilot_metrics (
            id, channel_id, channel_name, period_hours,
            pipeline_runs, pipeline_successes, pipeline_failures, pipeline_success_rate,
            topics_extracted, topics_new, topics_duplicated,
            posts_generated, posts_published, posts_failed, publish_success_rate,
            avg_pipeline_duration_seconds, avg_llm_generation_time, total_llm_calls,
            error_count, error_types, active_sources
        ) VALUES (
            :id, :channel_id, :channel_name, :period_hours,
            :pipeline_runs, :pipeline_successes, :pipeline_failures, :pipeline_success_rate,
            :topics_extracted, :topics_new, :topics_duplicated,
            :posts_generated, :posts_published, :posts_failed, :publish_success_rate,
            :avg_pipeline_duration_seconds, :avg_llm_generation_time, :total_llm_calls,
            :error_count, :error_types, :active_sources
        )
    """), {
        "id": metric_id,
        "channel_id": channel.id,
        "channel_name": channel.name,
        "period_hours": hours,
        "pipeline_runs": metrics["pipeline_runs"],
        "pipeline_successes": metrics["pipeline_successes"],
        "pipeline_failures": metrics["pipeline_failures"],
        "pipeline_success_rate": metrics["pipeline_success_rate"],
        "topics_extracted": metrics["topics_extracted"],
        "topics_new": metrics["topics_new"],
        "topics_duplicated": metrics["topics_duplicated"],
        "posts_generated": metrics["posts_generated"],
        "posts_published": metrics["posts_published"],
        "posts_failed": metrics["posts_failed"],
        "publish_success_rate": metrics["publish_success_rate"],
        "avg_pipeline_duration_seconds": metrics["avg_pipeline_duration_seconds"],
        "avg_llm_generation_time": metrics["avg_llm_generation_time"],
        "total_llm_calls": metrics["total_llm_calls"],
        "error_count": metrics["error_count"],
        "error_types": metrics["error_types"],
        "active_sources": metrics["active_sources"],
    })


def main():
    """Главная функция сбора метрик."""
    hours = 6
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    print(f"{'='*70}")
    print(f"📊 Pilot Metrics Collection (DB-based)")
    print(f"{'='*70}")
    print(f"Period: last {hours} hours")
    print(f"Cutoff: {cutoff.isoformat()} UTC")
    print(f"Timestamp: {datetime.utcnow().isoformat()} UTC")
    print(f"{'='*70}\n")
    
    db = SessionLocal()
    
    try:
        channels = db.query(ChannelORM).all()
        print(f"Collecting metrics for {len(channels)} channels...\n")
        
        collected = 0
        for channel in channels:
            try:
                metrics = collect_metrics_for_channel(db, channel, cutoff)
                
                # Пропускаем каналы без активности
                if metrics["posts_generated"] == 0 and metrics["pipeline_runs"] == 0:
                    print(f"  ⚪ {channel.name}: no activity")
                    continue
                
                save_metrics_to_db(db, channel, metrics, hours)
                collected += 1
                
                print(f"  ✅ {channel.name}:")
                print(f"     Posts: {metrics['posts_generated']} generated, "
                      f"{metrics['posts_published']} published, "
                      f"{metrics['posts_failed']} failed")
                print(f"     Success rate: {metrics['publish_success_rate']:.1f}%")
                print(f"     Pipeline runs: {metrics['pipeline_runs']}")
            except Exception as e:
                print(f"  ❌ {channel.name}: {e}")
                import traceback
                traceback.print_exc()
        
        db.commit()
        
        # Summary
        print(f"\n{'='*70}")
        print(f"✅ Metrics collection complete: {collected} channels with activity")
        print(f"{'='*70}")
        
        total_posts = db.execute(text("""
            SELECT SUM(posts_published) FROM pilot_metrics 
            WHERE collected_at > NOW() - INTERVAL '6 hours'
        """)).scalar() or 0
        
        total_runs = db.execute(text("""
            SELECT SUM(pipeline_runs) FROM pilot_metrics 
            WHERE collected_at > NOW() - INTERVAL '6 hours'
        """)).scalar() or 0
        
        total_errors = db.execute(text("""
            SELECT SUM(error_count) FROM pilot_metrics 
            WHERE collected_at > NOW() - INTERVAL '6 hours'
        """)).scalar() or 0
        
        print(f"\n📈 Summary (last 6h):")
        print(f"  Total pipeline runs: {total_runs}")
        print(f"  Total posts published: {total_posts}")
        print(f"  Total errors: {total_errors}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()