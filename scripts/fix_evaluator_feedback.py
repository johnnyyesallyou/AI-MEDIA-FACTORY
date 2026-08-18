import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')

# Ищем блок где устанавливается status = "needs_revision" и добавляем last_revision_reason
old_block = '''                    if result.is_approved:
                        item.status = "approved"
                        approved += 1
                    else:
                        item.status = "needs_revision"
                        rejected += 1'''

new_block = '''                    if result.is_approved:
                        item.status = "approved"
                        item.last_revision_reason = None
                        approved += 1
                    else:
                        item.status = "needs_revision"
                        # Сохраняем feedback от Evaluator, чтобы RevisionJob и WritingEngine
                        # знали, ЧТО именно нужно улучшить в тексте
                        item.last_revision_reason = getattr(result, 'feedback_for_regeneration', None) or "Качество ниже порога 80"
                        rejected += 1
                        logger.info("Item %s needs revision: %s", item.id, (item.last_revision_reason or "")[:100])'''

if old_block in s:
    s = s.replace(old_block, new_block)
    p.write_text(s, encoding='utf-8')
    print('OK: EvaluatorJob now writes feedback to last_revision_reason')
else:
    print('ERROR: pattern not found')