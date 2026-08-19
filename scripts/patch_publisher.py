import pathlib

# ?????? MangaPublishJob ??? ?????????? ???????????
p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
content = p.read_text(encoding="utf-8")

# 1. ????????? ??? ????? ??????? TelegraphPublisher
old_code = """            # ??????? Telegraph ????????
            telegraph_url = None
            try:"""

new_code = """            # ??????? Telegraph ????????
            telegraph_url = None
            logger.info(f"Attempting to create Telegraph page for: {item.headline}")
            try:"""

if old_code in content:
    content = content.replace(old_code, new_code)
    print("? Added logging before TelegraphPublisher call")

# 2. ????????? ??? ? except
old_except = """            except Exception as e:
                logger.warning(f"Telegraph failed, using short URL: {e}")"""

new_except = """            except Exception as e:
                logger.warning(f"Telegraph failed, using short URL: {e}")
                import traceback
                logger.warning(traceback.format_exc())"""

if old_except in content:
    content = content.replace(old_except, new_except)
    print("? Added traceback logging")

p.write_text(content, encoding="utf-8")
print("? MangaPublishJob patched")
