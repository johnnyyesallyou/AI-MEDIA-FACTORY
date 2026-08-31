"""Sprint 66.2: Connection pool monitoring (defensive)."""
try:
    from prometheus_client import Gauge
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

from core.database import engine

# Metrics (если prometheus доступен)
if HAS_PROMETHEUS:
    try:
        pool_checked_out = Gauge('db_pool_checked_out', 'Connections currently checked out')
    except ValueError:
        pool_checked_out = None  # уже зарегистрирован
else:
    pool_checked_out = None

# SQLAlchemy event listeners (safe)
try:
    from sqlalchemy import event

    @event.listens_for(engine, "checkout")
    def on_checkout(dbapi_conn, connection_rec, connection_proxy):
        if pool_checked_out:
            pool_checked_out.inc()

    @event.listens_for(engine, "checkin")
    def on_checkin(dbapi_conn, connection_rec):
        if pool_checked_out:
            pool_checked_out.dec()
except Exception as e:
    print(f"[db_metrics] event listeners not attached: {e}")


def get_pool_stats() -> dict:
    """Return current pool statistics (safe, no exceptions)."""
    try:
        pool = engine.pool
        stats = {
            "pool_class": type(pool).__name__,
        }
        # QueuePool-specific methods (safe getattr)
        for attr in ("size", "checkedout", "overflow", "checkedin"):
            fn = getattr(pool, attr, None)
            if callable(fn):
                try:
                    stats[attr] = fn()
                except Exception:
                    stats[attr] = None
        return stats
    except Exception as e:
        return {"error": str(e)}
