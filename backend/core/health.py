"""
Sprint 74.4: Health Checks для внешних API (Telegram/VK).

Проверяет доступность API и возвращает статус + латентность.
Используется оператором через /api/v1/reliability/health.
"""
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


async def check_telegram(bot_token: str) -> Dict[str, Any]:
    """Health check Telegram Bot API через getMe. Возвращает status + latency_ms."""
    import httpx

    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://api.telegram.org/bot{bot_token}/getMe"
            )
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        if resp.status_code == 200 and resp.json().get("ok"):
            return {"status": "ok", "latency_ms": latency_ms}
        return {"status": "error", "latency_ms": latency_ms, "detail": f"HTTP {resp.status_code}"}
    except Exception as e:
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {"status": "error", "latency_ms": latency_ms, "detail": str(e)}


async def check_vk(access_token: str, group_id: Optional[str] = None) -> Dict[str, Any]:
    """Health check VK API через groups.getById (или users.get если нет группы)."""
    import httpx

    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if group_id:
                resp = await client.post(
                    "https://api.vk.com/method/groups.getById",
                    data={
                        "group_id": str(group_id).replace("club", "").replace("public", ""),
                        "access_token": access_token,
                        "v": "5.199",
                    },
                )
            else:
                resp = await client.post(
                    "https://api.vk.com/method/users.get",
                    data={"access_token": access_token, "v": "5.199"},
                )
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        data = resp.json()
        if "error" in data:
            return {"status": "error", "latency_ms": latency_ms, "detail": data["error"].get("error_msg", "VK error")}
        return {"status": "ok", "latency_ms": latency_ms}
    except Exception as e:
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {"status": "error", "latency_ms": latency_ms, "detail": str(e)}


async def check_all(platforms: Optional[Dict[str, Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Проверить все платформы. platforms: {"telegram": {"bot_token": ...}, "vk": {"access_token": ..., "group_id": ...}}
    Если platforms пуст — возвращает {"status": "unknown", "detail": "No credentials provided"}.
    """
    if not platforms:
        return {"status": "unknown", "detail": "No credentials provided"}

    results: Dict[str, Any] = {}
    if "telegram" in platforms:
        results["telegram"] = await check_telegram(platforms["telegram"]["bot_token"])
    if "vk" in platforms:
        vk_cfg = platforms["vk"]
        results["vk"] = await check_vk(vk_cfg["access_token"], vk_cfg.get("group_id"))

    overall = "ok" if all(r.get("status") == "ok" for r in results.values()) else "error"
    return {"status": overall, "platforms": results}
