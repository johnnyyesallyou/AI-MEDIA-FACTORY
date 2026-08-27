import pathlib

p = pathlib.Path("/app/engines/preview_resolver.py")
c = p.read_text(encoding="utf-8")

# Ищем блок фильтрации зеркал
old_filter = '''    # Фильтруем только открытые зеркала
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

new_filter = '''    # Sprint 51: берём первое зеркало каждой страницы БЕЗ _mirror_open проверки
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
    return urls if urls else None'''

if old_filter in c:
    c = c.replace(old_filter, new_filter, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] preview_resolver: убрана _mirror_open проверка (берём первое зеркало)")
else:
    print("[!] Pattern not found")