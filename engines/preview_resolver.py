"""Preview Resolver v2 - без catbox fallback (блокируется IP).

Sprint 25: убираем retry на catbox для скорости.
"""
import logging
import time
import requests

logger = logging.getLogger(__name__)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
REFERER = {"Referer": "https://remanga.org/"}


def _mirror_open(url: str) -> bool:
    """Проверяет что зеркало отдаёт картинку БЕЗ Referer."""
    try:
        r = requests.get(url, headers=UA, timeout=5, stream=True)
        ok = r.status_code == 200 and "image" in r.headers.get("content-type", "")
        r.close()
        return ok
    except Exception:
        return False


def resolve_preview_pages(slug: str, limit: int = 5):
    """Возвращает только открытые зеркала ReManga (без catbox)."""
    try:
        r = requests.get(f"https://remanga.org/api/titles/{slug}/", headers=UA, timeout=10)
        content = r.json().get("content", {})
        first_chapter = content.get("first_chapter")
        if not first_chapter:
            return None
        chapter_id = first_chapter.get("id") if isinstance(first_chapter, dict) else first_chapter

        r2 = requests.get(f"https://remanga.org/api/titles/chapters/{chapter_id}/", headers=UA, timeout=10)
        pages = r2.json().get("content", {}).get("pages", [])
    except Exception as e:
        logger.error(f"preview fetch failed for {slug}: {e}")
        return None

    urls = []
    for idx, page_item in enumerate(pages[:limit]):
        mirrors = page_item if isinstance(page_item, list) else [page_item]
        links = [m.get("link") for m in mirrors if isinstance(m, dict) and m.get("link")]
        if not links:
            continue

        # Только открытые зеркала
        for link in links:
            if _mirror_open(link):
                urls.append(link)
                break

    logger.info(f"preview for {slug}: {len(urls)}/{limit} pages (open mirrors only)")
    return urls or None