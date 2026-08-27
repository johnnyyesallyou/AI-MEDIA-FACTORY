import pathlib

p = pathlib.Path("/app/engines/preview_resolver.py")
c = p.read_text(encoding="utf-8")

# Полностью переписываем функцию resolve_preview_pages
old_func = '''def resolve_preview_pages(slug: str, limit: int = 5):
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
    return urls or None'''

new_func = '''def resolve_preview_pages(slug: str, limit: int = 5):
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

    # Фильтруем только открытые зеркала
    urls = []
    for idx, page_item in enumerate(pages[:limit]):
        mirrors = page_item if isinstance(page_item, list) else [page_item]
        links = [m.get("link") for m in mirrors if isinstance(m, dict) and m.get("link")]
        if not links:
            continue

        for link in links:
            if _mirror_open(link):
                urls.append(link)
                break

    logger.info(f"preview for {slug}: {len(urls)}/{limit} pages (open mirrors only)")
    return urls if urls else None'''

if old_func in c:
    c = c.replace(old_func, new_func)
    p.write_text(c, encoding="utf-8")
    print("[OK] preview_resolver: добавлен Referer + логирование + fallback через chapters endpoint")
else:
    print("[!] Pattern not found")
    # Пробуем найти часть
    if 'def resolve_preview_pages' in c:
        print("[i] Функция существует, но код отличается — нужна ручная правка")