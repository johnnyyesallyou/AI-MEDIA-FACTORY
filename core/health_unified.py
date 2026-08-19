"""Unified Health Service - Sprint 41.

Единая точка мониторинга всех компонентов системы.
Возвращает статус:
- Database (postgres)
- Research (5 sources)
- Publishers (Telegram, VK)
- Automation (scheduler, jobs)
- Prometheus (metrics endpoint)
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from sqlalchemy import text, func
import requests

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.content_orm import ContentORM
from core.models.analytics import PostMetric


logger = logging.getLogger(__name__)


class ComponentStatus:
    """Статус компонента."""
    OK = "ok"
    DEGRADED = "degraded"
    ERROR = "error"
    UNKNOWN = "unknown"


class UnifiedHealthService:
    """Unified health monitoring для всех компонентов системы."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cache = {}
        self._cache_ttl = 10  # секунд

    def get_overall_status(self) -> Dict[str, Any]:
        """Возвращает общий статус системы."""
        components = {
            "database": self.check_database(),
            "sources": self.check_sources(),
            "publishers": self.check_publishers(),
            "automation": self.check_automation(),
            "metrics": self.check_metrics(),
        }

        # Общий статус — худший из всех
        statuses = [c["status"] for c in components.values()]
        if ComponentStatus.ERROR in statuses:
            overall = ComponentStatus.ERROR
        elif ComponentStatus.DEGRADED in statuses:
            overall = ComponentStatus.DEGRADED
        elif all(s == ComponentStatus.OK for s in statuses):
            overall = ComponentStatus.OK
        else:
            overall = ComponentStatus.UNKNOWN

        return {
            "status": overall,
            "timestamp": datetime.utcnow().isoformat(),
            "components": components,
            "summary": {
                "ok": sum(1 for s in statuses if s == ComponentStatus.OK),
                "degraded": sum(1 for s in statuses if s == ComponentStatus.DEGRADED),
                "error": sum(1 for s in statuses if s == ComponentStatus.ERROR),
            }
        }

    def check_database(self) -> Dict[str, Any]:
        """Проверка подключения к БД."""
        start = time.time()
        try:
            db = SessionLocal()
            try:
                # Простой ping
                db.execute(text("SELECT 1"))
                
                # Получаем базовую статистику
                channels_count = db.query(func.count(ChannelORM.id)).scalar() or 0
                content_count = db.query(func.count(ContentORM.id)).scalar() or 0
                metrics_count = db.query(func.count(PostMetric.id)).scalar() or 0

                return {
                    "status": ComponentStatus.OK,
                    "latency_ms": round((time.time() - start) * 1000, 2),
                    "details": {
                        "channels": channels_count,
                        "content": content_count,
                        "metrics": metrics_count,
                    }
                }
            finally:
                db.close()
        except Exception as e:
            return {
                "status": ComponentStatus.ERROR,
                "latency_ms": round((time.time() - start) * 1000, 2),
                "error": str(e),
            }

    def check_sources(self) -> Dict[str, Any]:
        """Проверка источников (ReManga, MangaDex, ReadManga, AniList, Habr)."""
        sources = {
            "ReManga": "https://remanga.org/api/titles/?ordering=-id&count=1",
            "MangaDex": "https://api.mangadex.org/manga?limit=1",
            "AniList": "https://graphql.anilist.co",  # GraphQL endpoint
            "Habr": "https://habr.com/ru/rss/articles/?fl=ru",  # RSS
            "ReadManga": "https://readmanga.io",
        }

        results = {}
        ok_count = 0

        for name, url in sources.items():
            start = time.time()
            try:
                if name == "AniList":
                    # GraphQL ping
                    r = requests.post(url, json={
                        "query": "{ Media(type: ANIME) { id } }"
                    }, timeout=5)
                elif name == "Habr":
                    # RSS feed
                    r = requests.get(url, timeout=5)
                else:
                    r = requests.get(url, timeout=5)

                if r.status_code in (200, 301, 302):
                    results[name] = {
                        "status": ComponentStatus.OK,
                        "latency_ms": round((time.time() - start) * 1000, 2),
                        "status_code": r.status_code,
                    }
                    ok_count += 1
                else:
                    results[name] = {
                        "status": ComponentStatus.ERROR,
                        "latency_ms": round((time.time() - start) * 1000, 2),
                        "status_code": r.status_code,
                    }
            except Exception as e:
                results[name] = {
                    "status": ComponentStatus.ERROR,
                    "latency_ms": round((time.time() - start) * 1000, 2),
                    "error": type(e).__name__,
                }

        # Общий статус sources
        total = len(sources)
        if ok_count == total:
            status = ComponentStatus.OK
        elif ok_count > 0:
            status = ComponentStatus.DEGRADED
        else:
            status = ComponentStatus.ERROR

        return {
            "status": status,
            "available": ok_count,
            "total": total,
            "details": results,
        }

    def check_publishers(self) -> Dict[str, Any]:
        """Проверка publishers (Telegram, VK)."""
        import os
        
        publishers = {}
        ok_count = 0

        # Telegram
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if tg_token and tg_token != "your_telegram_bot_token_here":
            try:
                r = requests.get(
                    f"https://api.telegram.org/bot{tg_token}/getMe",
                    timeout=5
                )
                if r.status_code == 200 and r.json().get("ok"):
                    publishers["Telegram"] = {
                        "status": ComponentStatus.OK,
                        "bot": r.json()["result"].get("username"),
                    }
                    ok_count += 1
                else:
                    publishers["Telegram"] = {
                        "status": ComponentStatus.ERROR,
                        "error": "getMe failed",
                    }
            except Exception as e:
                publishers["Telegram"] = {
                    "status": ComponentStatus.ERROR,
                    "error": type(e).__name__,
                }
        else:
            publishers["Telegram"] = {
                "status": ComponentStatus.DEGRADED,
                "error": "Token not configured",
            }

        # VK
        vk_token = os.getenv("VK_TOKEN", "")
        if vk_token and vk_token != "your_vk_group_token_here":
            try:
                r = requests.get(
                    "https://api.vk.com/method/groups.getSettings",
                    params={
                        "access_token": vk_token,
                        "v": "5.131",
                    },
                    timeout=5
                )
                if r.status_code == 200:
                    publishers["VK"] = {
                        "status": ComponentStatus.OK,
                    }
                    ok_count += 1
                else:
                    publishers["VK"] = {
                        "status": ComponentStatus.ERROR,
                        "status_code": r.status_code,
                    }
            except Exception as e:
                publishers["VK"] = {
                    "status": ComponentStatus.ERROR,
                    "error": type(e).__name__,
                }
        else:
            publishers["VK"] = {
                "status": ComponentStatus.DEGRADED,
                "error": "Token not configured",
            }

        total = len(publishers)
        if ok_count == total:
            status = ComponentStatus.OK
        elif ok_count > 0:
            status = ComponentStatus.DEGRADED
        else:
            status = ComponentStatus.ERROR

        return {
            "status": status,
            "available": ok_count,
            "total": total,
            "details": publishers,
        }

    def check_automation(self) -> Dict[str, Any]:
        """Проверка automation (scheduler, active channels)."""
        try:
            db = SessionLocal()
            try:
                # Каналы с automation
                total = db.query(func.count(ChannelORM.id)).scalar() or 0
                active = db.query(func.count(ChannelORM.id)).filter(
                    ChannelORM.automation_enabled == True
                ).scalar() or 0
                
                # Недавняя активность
                recent_cutoff = datetime.utcnow() - timedelta(hours=24)
                recent_posts = db.query(func.count(ContentORM.id)).filter(
                    ContentORM.published_at >= recent_cutoff
                ).scalar() or 0

                if active > 0:
                    status = ComponentStatus.OK
                elif total > 0:
                    status = ComponentStatus.DEGRADED
                else:
                    status = ComponentStatus.UNKNOWN

                return {
                    "status": status,
                    "channels": {
                        "total": total,
                        "active": active,
                        "paused": total - active,
                    },
                    "recent_posts_24h": recent_posts,
                }
            finally:
                db.close()
        except Exception as e:
            return {
                "status": ComponentStatus.ERROR,
                "error": str(e),
            }

    def check_metrics(self) -> Dict[str, Any]:
        """Проверка Prometheus metrics endpoint."""
        start = time.time()
        try:
            r = requests.get("http://localhost:8000/metrics", timeout=5)
            if r.status_code == 200 and "amf_" in r.text:
                # Считаем количество метрик
                metrics_count = len([l for l in r.text.split('\n') if l.startswith('amf_') and not l.startswith('#')])
                return {
                    "status": ComponentStatus.OK,
                    "latency_ms": round((time.time() - start) * 1000, 2),
                    "metrics_count": metrics_count,
                }
            else:
                return {
                    "status": ComponentStatus.ERROR,
                    "latency_ms": round((time.time() - start) * 1000, 2),
                    "status_code": r.status_code,
                }
        except Exception as e:
            return {
                "status": ComponentStatus.ERROR,
                "error": type(e).__name__,
            }