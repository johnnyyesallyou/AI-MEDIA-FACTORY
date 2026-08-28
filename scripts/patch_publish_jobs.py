import pathlib

files = [
    pathlib.Path("backend/automation/jobs/manga_publish_job.py"),
    pathlib.Path("backend/automation/jobs/news_publish_job.py"),
    pathlib.Path("backend/automation/jobs/anime_publish_job.py"),
]

old = '''        if result.get("status") == "success":
            item.telegram_message_id = str(result.get("message_id", ""))
            db.commit()

        return result
'''

new = '''        if result.get("status") == "success":
            item.telegram_message_id = str(result.get("message_id", ""))

            # Sprint 58: record publication in post_history for Learning Loop
            try:
                from engines.post_history_recorder import record_post_history
                record_post_history(
                    db=db,
                    channel=locals().get("channel") or locals().get("manga_channel") or locals().get("anime_channel") or locals().get("news_channel"),
                    item=item,
                    publication=publication,
                    result=result,
                )
            except Exception as history_e:
                self.logger.warning(f"Failed to record post_history for item={getattr(item, 'id', None)}: {history_e}")

            db.commit()

        return result
'''

for p in files:
    if not p.exists():
        print(f"[skip] {p} not found")
        continue

    c = p.read_text(encoding="utf-8")

    if "record_post_history(" in c:
        print(f"[i] already patched: {p}")
        continue

    if old not in c:
        print(f"[!] pattern not found in {p}")
        continue

    c = c.replace(old, new)
    p.write_text(c, encoding="utf-8")
    print(f"[OK] patched {p}")