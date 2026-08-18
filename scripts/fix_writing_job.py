import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')

# Ищем блок где сохраняется драфт и добавляем проверку на пустоту
old_save = '''                    item.draft_text = clean_text
                    item.status = "draft"
                    db.commit()
                    processed += 1
                    logger.info("Written item=%s", item.id)'''

new_save = '''                    # WritingEngine v1.5: не сохраняем пустые или слишком короткие драфты
                    if not clean_text or len(clean_text.strip()) < 50:
                        item.status = "needs_revision"
                        item.last_revision_reason = f"Generated text too short ({len(clean_text.strip())} chars). OutputGuard вернул пустой текст."
                        db.commit()
                        logger.warning("Skip short draft item=%s len=%s", item.id, len(clean_text.strip()) if clean_text else 0)
                        failed += 1
                        continue
                    
                    item.draft_text = clean_text
                    item.status = "draft"
                    db.commit()
                    processed += 1
                    logger.info("Written item=%s len=%s", item.id, len(clean_text))'''

if old_save in s:
    s = s.replace(old_save, new_save)
    p.write_text(s, encoding='utf-8')
    print('OK: WritingJob теперь не сохраняет пустые драфты (min 50 символов)')
else:
    print('ERROR: паттерн сохранения не найден')