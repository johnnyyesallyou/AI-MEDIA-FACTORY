import pathlib, re as _re

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

changed = False

# 1. Фильтр тайтлов без кириллицы (вставляем после _get_max_chapter)
marker = "max_item = self._get_max_chapter(title_items)"
if marker in c and "RU-only" not in c:
    block = marker + '''

                # Sprint 19: RU-only фильтр - пропускаем тайтлы без кириллицы
                meta_check = self._parse_metadata(max_item.source_text)
                title_check = meta_check.get("manga_title_name", "") or ""
                if not re.search(r"[а-яА-ЯёЁ]", title_check):
                    self.logger.info(f"Skipping EN-only title: {title_check[:50]}")
                    for rel in title_items:
                        rel.status = "skipped_en"
                    db.commit()
                    continue'''
    c = c.replace(marker, block, 1)
    changed = True
    print("✅ RU-only title filter added")

# 2. Убираем английские описания
old_desc = '        description = metadata.get("manga_description", "")'
new_desc = '''        description = metadata.get("manga_description", "")
        # Sprint 19: только русские описания
        if description and not re.search(r"[а-яА-ЯёЁ]", description):
            description = ""'''
if old_desc in c and "только русские описания" not in c:
    c = c.replace(old_desc, new_desc, 1)
    changed = True
    print("✅ EN description filter added")

if changed:
    p.write_text(c, encoding="utf-8")
    import ast
    ast.parse(c)
    print("✅ Syntax OK")
else:
    print("ℹ️ Already patched or marker not found")