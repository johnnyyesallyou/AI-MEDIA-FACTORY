"""Sprint 73.1: Pipeline Run Metrics API.

История прогонов Universal Pipeline, агрегаты по стадиям и
поиск самых медленных каналов (кандидаты на оптимизацию).
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.database import get_db
from core.models.pipeline_run_metrics_orm import PipelineRunMetrics

router = APIRouter(prefix="/metrics/pipeline", tags=["pipeline-metrics"])

# Sprint 73.4: пороги алертов (наследуют Sprint 72.6: task timeout = 1800s)
DEFAULT_TIMEOUT_MS = 1_800_000
# Sprint 73.2 baseline: LLM ~74-81s на пост; 2x = деградация
DEFAULT_LLM_BASELINE_MS = 80_000
DEFAULT_LLM_DEGRADATION_FACTOR = 2.0


def _to_dict(m: PipelineRunMetrics) -> dict:
    return {
        "id": m.id,
        "channel_id": m.channel_id,
        "channel_name": m.channel_name,
        "execution_id": m.execution_id,
        "stage_timings_ms": {
            "research": m.research_ms,
            "writing": m.writing_ms,
            "media": m.media_ms,
            "publishing": m.publishing_ms,
        },
        "total_ms": m.total_ms,
        "topics": {
            "found": m.topics_found,
            "generated": m.topics_generated,
            "published": m.topics_published,
        },
        "errors_count": m.errors_count,
        "success": m.success == "true",
        # Sprint 73.3: LLM-метрики прогона
        "llm": {
            "llm_calls": m.llm_calls or 0,
            "llm_errors": m.llm_errors or 0,
            "llm_latency_ms": m.llm_latency_ms or 0,
            "tokens_in": m.tokens_in or 0,
            "tokens_out": m.tokens_out or 0,
            "llm_model": m.llm_model,
        },
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


# === Sprint 73.4: Dashboard + Alerts ===
# ВАЖНО: односегментные маршруты объявлены ДО /{channel_id}, иначе FastAPI
# сматчит /alerts и /trends как channel_id.


def _percentile(values: list, pct: float) -> float:
    """Линейный перцентиль (portable, без numpy) по списку значений."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return float(s[0])
    k = (len(s) - 1) * pct
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return float(s[f] + (s[c] - s[f]) * (k - f))


def _avg_llm_latency_row(m) -> int:
    """Средняя латентность на один LLM-вызов (защита от деления на ноль)."""
    calls = int(m.llm_calls or 0)
    if calls <= 0:
        return 0
    return round(int(m.llm_latency_ms or 0) / calls)


@router.get("/health/overview")
async def get_health_overview(
    window_hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """Sprint 73.4: health по каналам за окно — success rate, P50/P95, LLM-метрики.

    Статус канала: healthy | warning | critical.
    """
    cutoff = datetime.utcnow() - timedelta(hours=window_hours)
    rows = (
        db.query(PipelineRunMetrics)
        .filter(PipelineRunMetrics.created_at >= cutoff)
        .order_by(PipelineRunMetrics.created_at.asc())
        .all()
    )

    channels: dict = {}
    for m in rows:
        ch = channels.setdefault(
            m.channel_id,
            {
                "channel_id": m.channel_id,
                "channel_name": m.channel_name or m.channel_id,
                "runs": 0,
                "success_runs": 0,
                "topics_published": 0,
                "errors_count": 0,
                "total_ms": [],
                "llm_calls": 0,
                "llm_errors": 0,
                "llm_latency_ms": 0,
                "tokens_in": 0,
                "tokens_out": 0,
                "llm_model": None,
                "last_run_at": None,
            },
        )
        ch["runs"] += 1
        if m.success == "true":
            ch["success_runs"] += 1
        ch["topics_published"] += int(m.topics_published or 0)
        ch["errors_count"] += int(m.errors_count or 0)
        if m.total_ms is not None:
            ch["total_ms"].append(int(m.total_ms))
        ch["llm_calls"] += int(m.llm_calls or 0)
        ch["llm_errors"] += int(m.llm_errors or 0)
        ch["llm_latency_ms"] += int(m.llm_latency_ms or 0)
        ch["tokens_in"] += int(m.tokens_in or 0)
        ch["tokens_out"] += int(m.tokens_out or 0)
        if m.llm_model:
            ch["llm_model"] = m.llm_model
        if m.created_at is not None:
            iso = m.created_at.isoformat()
            if ch["last_run_at"] is None or iso > ch["last_run_at"]:
                ch["last_run_at"] = iso

    overview = []
    for ch in channels.values():
        runs = ch["runs"]
        success_rate = round(100.0 * ch["success_runs"] / runs, 1) if runs else 0.0
        totals = ch.pop("total_ms")
        avg_total = round(sum(totals) / len(totals)) if totals else 0
        p50 = round(_percentile(totals, 0.50))
        p95 = round(_percentile(totals, 0.95))
        llm_avg = (
            round(ch["llm_latency_ms"] / ch["llm_calls"]) if ch["llm_calls"] > 0 else 0
        )
        if success_rate < 50.0 or ch["errors_count"] > runs:
            status = "critical"
        elif success_rate < 100.0 or ch["errors_count"] > 0 or p95 > DEFAULT_TIMEOUT_MS:
            status = "warning"
        else:
            status = "healthy"
        overview.append(
            {
                "channel_id": ch["channel_id"],
                "channel_name": ch["channel_name"],
                "status": status,
                "runs": runs,
                "success_rate": success_rate,
                "topics_published": ch["topics_published"],
                "errors_count": ch["errors_count"],
                "total_ms": {"avg": avg_total, "p50": p50, "p95": p95},
                "llm": {
                    "llm_calls": ch["llm_calls"],
                    "llm_errors": ch["llm_errors"],
                    "llm_avg_latency_ms": llm_avg,
                    "tokens_in": ch["tokens_in"],
                    "tokens_out": ch["tokens_out"],
                    "llm_model": ch["llm_model"],
                },
                "last_run_at": ch["last_run_at"],
            }
        )
    overview.sort(key=lambda x: x["total_ms"]["avg"], reverse=True)
    return {
        "window_hours": window_hours,
        "channels": overview,
        "count": len(overview),
    }


@router.get("/alerts")
async def get_alerts(
    window_hours: int = Query(24, ge=1, le=168),
    timeout_ms: int = Query(DEFAULT_TIMEOUT_MS, ge=1),
    llm_baseline_ms: int = Query(DEFAULT_LLM_BASELINE_MS, ge=1),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Sprint 73.4: активные алерты по метрикам пайплайна и failures.

    Типы: run_failure, timeout, llm_degradation, stale_channel, failure (unresolved).
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=window_hours)
    alerts: list = []

    rows = (
        db.query(PipelineRunMetrics)
        .filter(PipelineRunMetrics.created_at >= cutoff)
        .order_by(PipelineRunMetrics.created_at.desc())
        .all()
    )

    by_channel: dict = {}
    for m in rows:
        by_channel.setdefault(m.channel_id, []).append(m)

    def _alert(kind, severity, ch_id, ch_name, message, execution_id=None, value=None):
        alerts.append(
            {
                "type": kind,
                "severity": severity,
                "channel_id": ch_id,
                "channel_name": ch_name,
                "message": message,
                "execution_id": execution_id,
                "value": value,
                "created_at": now.isoformat(),
            }
        )

    for ch_id, runs in by_channel.items():
        name = next((r.channel_name or ch_id for r in runs), ch_id)

        failed = [r for r in runs if r.success != "true"]
        if failed:
            _alert(
                "run_failure",
                "critical",
                ch_id,
                name,
                f"{len(failed)} из {len(runs)} прогонов завершились с ошибкой за {window_hours}ч",
                execution_id=failed[0].execution_id,
                value={"failed_runs": len(failed), "total_runs": len(runs)},
            )

        for r in runs:
            if r.total_ms is not None and int(r.total_ms) >= timeout_ms:
                _alert(
                    "timeout",
                    "critical",
                    ch_id,
                    name,
                    f"Прогон {r.execution_id or r.id} превысил timeout "
                    f"({int(r.total_ms) / 1000:.0f}s >= {timeout_ms / 1000:.0f}s)",
                    execution_id=r.execution_id,
                    value={"total_ms": int(r.total_ms), "threshold_ms": timeout_ms},
                )
                break  # один timeout-алерт на канал достаточно

        llm_err_runs = [r for r in runs if int(r.llm_errors or 0) > 0]
        if llm_err_runs:
            _alert(
                "llm_degradation",
                "warning",
                ch_id,
                name,
                f"LLM-ошибки в {len(llm_err_runs)} прогон(ах) за {window_hours}ч",
                execution_id=llm_err_runs[0].execution_id,
                value={"llm_errors": sum(int(r.llm_errors or 0) for r in llm_err_runs)},
            )

        degraded = [
            r
            for r in runs
            if int(r.llm_calls or 0) > 0
            and _avg_llm_latency_row(r) > llm_baseline_ms * DEFAULT_LLM_DEGRADATION_FACTOR
        ]
        if degraded:
            worst = max(degraded, key=_avg_llm_latency_row)
            _alert(
                "llm_degradation",
                "warning",
                ch_id,
                name,
                f"LLM-латентность {_avg_llm_latency_row(worst) / 1000:.0f}s/вызов > порога "
                f"{llm_baseline_ms * DEFAULT_LLM_DEGRADATION_FACTOR / 1000:.0f}s",
                execution_id=worst.execution_id,
                value={
                    "avg_llm_latency_ms": _avg_llm_latency_row(worst),
                    "baseline_ms": llm_baseline_ms,
                },
            )

    # stale: каналы, известные в метриках вообще, но без прогонов за окно
    known = (
        db.query(PipelineRunMetrics.channel_id, PipelineRunMetrics.channel_name)
        .distinct()
        .all()
    )
    active_ids = set(by_channel.keys())
    for ch_id, ch_name in known:
        if ch_id not in active_ids:
            _alert(
                "stale_channel",
                "warning",
                ch_id,
                ch_name or ch_id,
                f"Нет прогонов за последние {window_hours}ч",
                value={"window_hours": window_hours},
            )

    # unresolved failures из pipeline_failures (Sprint 66.5)
    try:
        from core.models.pipeline_failure_orm import PipelineFailure

        unresolved = (
            db.query(PipelineFailure)
            .filter(PipelineFailure.resolved == False)  # noqa: E712
            .order_by(PipelineFailure.created_at.desc())
            .limit(limit)
            .all()
        )
        for f in unresolved:
            alerts.append(
                {
                    "type": "failure",
                    "severity": "critical",
                    "channel_id": f.channel_id,
                    "channel_name": f.channel_id,
                    "message": f"{f.pipeline}/{f.job}: {f.error_type} — {(f.error_message or '')[:200]}",
                    "execution_id": f.execution_id,
                    "value": {"error_type": f.error_type, "attempt": f.attempt},
                    "created_at": f.created_at.isoformat() if f.created_at else None,
                }
            )
    except Exception:
        # таблица failures может отсутствовать в тестовых SQLite-базах
        pass

    severity_order = {"critical": 0, "warning": 1, "info": 2}
    alerts.sort(
        key=lambda a: (severity_order.get(a["severity"], 3), a["created_at"] or "")
    )
    return {"alerts": alerts[:limit], "count": len(alerts[:limit])}


@router.get("/trends")
async def get_trends(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """Sprint 73.4: почасовые тренды прогонов — для исторических графиков."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    rows = (
        db.query(PipelineRunMetrics)
        .filter(PipelineRunMetrics.created_at >= cutoff)
        .all()
    )

    buckets: dict = {}
    for m in rows:
        if m.created_at is None:
            continue
        hour_key = m.created_at.replace(minute=0, second=0, microsecond=0)
        b = buckets.setdefault(
            hour_key,
            {
                "runs": 0,
                "published": 0,
                "errors": 0,
                "total_ms": [],
                "llm_latency_ms": 0,
                "llm_calls": 0,
            },
        )
        b["runs"] += 1
        b["published"] += int(m.topics_published or 0)
        b["errors"] += int(m.errors_count or 0)
        if m.total_ms is not None:
            b["total_ms"].append(int(m.total_ms))
        b["llm_latency_ms"] += int(m.llm_latency_ms or 0)
        b["llm_calls"] += int(m.llm_calls or 0)

    trends = []
    for hour_key in sorted(buckets.keys()):
        b = buckets[hour_key]
        totals = b["total_ms"]
        trends.append(
            {
                "hour": hour_key.isoformat(),
                "runs": b["runs"],
                "published": b["published"],
                "errors": b["errors"],
                "avg_total_ms": round(sum(totals) / len(totals)) if totals else 0,
                "avg_llm_latency_ms": (
                    round(b["llm_latency_ms"] / b["llm_calls"])
                    if b["llm_calls"] > 0
                    else 0
                ),
            }
        )
    return {"hours": hours, "trends": trends, "count": len(trends)}


@router.get("/{channel_id}")
async def get_pipeline_metrics(channel_id: str, limit: int = Query(10, le=100), db: Session = Depends(get_db)):
    """История последних N прогонов пайплайна для канала."""
    rows = (
        db.query(PipelineRunMetrics)
        .filter(PipelineRunMetrics.channel_id == channel_id)
        .order_by(PipelineRunMetrics.created_at.desc())
        .limit(limit)
        .all()
    )
    return {"channel_id": channel_id, "runs": [_to_dict(m) for m in rows], "count": len(rows)}


@router.get("/summary/all")
async def get_pipeline_summary(limit: int = Query(50, le=500), db: Session = Depends(get_db)):
    """Сводка по всем каналам: средние тайминги по стадиям (по последним прогонам)."""
    rows = (
        db.query(
            PipelineRunMetrics.channel_id,
            func.count(PipelineRunMetrics.id).label("runs"),
            func.avg(PipelineRunMetrics.research_ms).label("avg_research"),
            func.avg(PipelineRunMetrics.writing_ms).label("avg_writing"),
            func.avg(PipelineRunMetrics.media_ms).label("avg_media"),
            func.avg(PipelineRunMetrics.publishing_ms).label("avg_publishing"),
            func.avg(PipelineRunMetrics.total_ms).label("avg_total"),
            func.sum(PipelineRunMetrics.topics_published).label("published"),
            # Sprint 73.4: LLM-агрегаты (follow-up из 73.3)
            func.sum(PipelineRunMetrics.llm_calls).label("llm_calls"),
            func.sum(PipelineRunMetrics.llm_errors).label("llm_errors"),
            func.sum(PipelineRunMetrics.llm_latency_ms).label("llm_latency_ms"),
            func.sum(PipelineRunMetrics.tokens_in).label("tokens_in"),
            func.sum(PipelineRunMetrics.tokens_out).label("tokens_out"),
        )
        .group_by(PipelineRunMetrics.channel_id)
        .all()
    )
    # limit применяем к средним по убыванию avg_total — самые медленные сверху
    summary = [
        {
            "channel_id": r.channel_id,
            "runs": int(r.runs or 0),
            "avg_ms": {
                "research": round(float(r.avg_research or 0)),
                "writing": round(float(r.avg_writing or 0)),
                "media": round(float(r.avg_media or 0)),
                "publishing": round(float(r.avg_publishing or 0)),
                "total": round(float(r.avg_total or 0)),
            },
            "topics_published": int(r.published or 0),
            "llm": {
                "llm_calls": int(r.llm_calls or 0),
                "llm_errors": int(r.llm_errors or 0),
                # средняя латентность на один LLM-вызов
                "llm_avg_latency_ms": round(
                    float(r.llm_latency_ms or 0) / float(r.llm_calls or 1)
                ),
                "tokens_in": int(r.tokens_in or 0),
                "tokens_out": int(r.tokens_out or 0),
            },
        }
        for r in rows
    ]
    summary.sort(key=lambda x: x["avg_ms"]["total"], reverse=True)
    return {"channels": summary[:limit], "count": len(summary)}


@router.get("/slowest/top")
async def get_slowest_channels(limit: int = Query(5, le=50), db: Session = Depends(get_db)):
    """Самые медленные каналы (по среднему total_ms) — кандидаты на оптимизацию."""
    rows = (
        db.query(
            PipelineRunMetrics.channel_id,
            PipelineRunMetrics.channel_name,
            func.avg(PipelineRunMetrics.total_ms).label("avg_total"),
            func.avg(PipelineRunMetrics.writing_ms).label("avg_writing"),
            func.count(PipelineRunMetrics.id).label("runs"),
        )
        .group_by(PipelineRunMetrics.channel_id, PipelineRunMetrics.channel_name)
        .order_by(func.avg(PipelineRunMetrics.total_ms).desc())
        .limit(limit)
        .all()
    )
    return {
        "slowest": [
            {
                "channel_id": r.channel_id,
                "channel_name": r.channel_name,
                "runs": int(r.runs or 0),
                "avg_total_ms": round(float(r.avg_total or 0)),
                "avg_writing_ms": round(float(r.avg_writing or 0)),
            }
            for r in rows
        ]
    }
