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
    """Возвращает только открытые зеркала ReManga (без catbox). Sprint 51 fix: +Referer +logging +fallback."""
    headers = {**UA, **REFERER}  # Sprint 51: добавляем Referer для ReManga API
    
    try:
        # Step 1: получаем инфо о тайтле
        r = requests.get(f"https://remanga.org/api/titles/{slug}/", headers=headers, timeout=10)
        logger.info(f"ReManga API status for {slug}: {r.status_code}")
        
        if r.status_code != 200:
            logger.warning(f"ReManga API returned {r.status_code} for slug={slug}")
            return None
        
        data = r.json()
        content = data.get("content", {})
        logger.info(f"ReManga content keys: {list(content.keys())[:10]}")
        
        # Ищем первую главу
        first_chapter = content.get("first_chapter")
        chapter_id = None
        
        if first_chapter:
            chapter_id = first_chapter.get("id") if isinstance(first_chapter, dict) else first_chapter
            logger.info(f"first_chapter found: id={chapter_id}")
        else:
            # Sprint 51 fallback: пробуем chapters endpoint
            logger.info(f"first_chapter not found, trying chapters endpoint for {slug}")
            chapters_resp = requests.get(
                f"https://remanga.org/api/titles/{slug}/chapters",
                headers=headers,
                timeout=10,
            )
            if chapters_resp.status_code == 200:
                chapters_list = chapters_resp.json().get("content", [])
                if chapters_list and isinstance(chapters_list, list):
                    # Берём последнюю (самую новую) главу
                    chapter_id = chapters_list[-1].get("id")
                    logger.info(f"Got chapter_id from chapters list: {chapter_id}")
        
        if not chapter_id:
            logger.warning(f"Could not find any chapter for slug={slug}")
            return None
        
        # Step 2: получаем страницы главы
        r2 = requests.get(
            f"https://remanga.org/api/titles/chapters/{chapter_id}/",
            headers=headers,
            timeout=10,
        )
        logger.info(f"Chapter API status: {r2.status_code}")
        
        if r2.status_code != 200:
            logger.warning(f"Chapter API returned {r2.status_code}")
            return None
        
        pages = r2.json().get("content", {}).get("pages", [])
        logger.info(f"Chapter has {len(pages)} pages total")
        
    except Exception as e:
        logger.error(f"preview fetch failed for {slug}: {e}")
        return None

    # Sprint 51: берём первое зеркало каждой страницы БЕЗ _mirror_open проверки
    # (ReManga API уже возвращает рабочие URL, _mirror_open блокируется IP)
    urls = []
    for idx, page_item in enumerate(pages[:limit]):
        mirrors = page_item if isinstance(page_item, list) else [page_item]
        links = [m.get("link") for m in mirrors if isinstance(m, dict) and m.get("link")]
        if links:
            # Берём первое зеркало
            urls.append(links[0])
            logger.info(f"  page {idx+1}: {links[0][:80]}")

    logger.info(f"preview for {slug}: {len(urls)}/{limit} pages fetched")
    return urls if urls else None