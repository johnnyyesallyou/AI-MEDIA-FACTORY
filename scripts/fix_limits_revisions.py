import pathlib

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')
changes = []

# 1. Увеличиваем limit с 10 до 50 в WritingJob
if 'items = repo.list_all(status="research", limit=10)' in s:
    s = s.replace(
        'items = repo.list_all(status="research", limit=10)',
        'items = repo.list_all(status="research", limit=50)'
    )
    changes.append('WritingJob limit 10->50')

# 2. Увеличиваем limit с 10 до 50 в EvaluatorJob
if 'items = repo.list_all(status="draft", limit=10)' in s:
    s = s.replace(
        'items = repo.list_all(status="draft", limit=10)',
        'items = repo.list_all(status="draft", limit=50)'
    )
    changes.append('EvaluatorJob limit 10->50')

# 3. Увеличиваем limit с 10 до 50 в RevisionJob (файл revision_job.py)
rp = pathlib.Path('./backend/automation/jobs/revision_job.py')
rs = rp.read_text(encoding='utf-8-sig').replace('\ufeff', '')
if 'items = repo.list_all(status="needs_revision", limit=10)' in rs:
    rs = rs.replace(
        'items = repo.list_all(status="needs_revision", limit=10)',
        'items = repo.list_all(status="needs_revision", limit=50)'
    )
    rp.write_text(rs, encoding='utf-8')
    changes.append('RevisionJob limit 10->50')

# 4. Добавляем MAX_REVISION_COUNT = 3 в начале RevisionJob.run
if 'MAX_REVISION_COUNT' not in rs:
    old_block = '''    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("revision")

        logger.info("=== REVISION JOB STARTED ===")'''
    
    new_block = '''    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("revision")

        logger.info("=== REVISION JOB STARTED ===")
        MAX_REVISION_COUNT = 3  # Защита от бесконечного цикла'''
    
    rs = rs.replace(old_block, new_block)
    
    # 5. В цикле обработки items: если revision_count >= MAX, помечаем как rejected
    old_revision_logic = '''            for item in items:
                item.revision_count = (getattr(item, 'revision_count', 0) or 0) + 1
                item.status = "draft" # Возвращаем на черновик для повторной оценки
                processed += 1'''
    
    new_revision_logic = '''            rejected_too_many = 0
            for item in items:
                current_count = (getattr(item, 'revision_count', 0) or 0) + 1
                item.revision_count = current_count
                
                if current_count >= MAX_REVISION_COUNT:
                    # Защита от бесконечного цикла - помечаем как rejected
                    item.status = "rejected"
                    item.last_revision_reason = f"Превышен лимит итераций ({MAX_REVISION_COUNT}). Текст не улучшился."
                    rejected_too_many += 1
                    logger.info("Item %s rejected: too many revisions (%d)", item.id, current_count)
                else:
                    # Возвращаем на черновик для повторной оценки
                    item.status = "draft"
                    processed += 1
            
            if rejected_too_many > 0:
                logger.info("Rejected %d items due to max revision count", rejected_too_many)'''
    
    if old_revision_logic in rs:
        rs = rs.replace(old_revision_logic, new_revision_logic)
        
        # Обновляем p_logger.finish чтобы включить rejected
        old_finish = 'p_logger.finish("success", details=f"Revised {processed} items")'
        new_finish = 'p_logger.finish("success", details=f"Revised {processed}, rejected {rejected_too_many} (max revisions)")'
        rs = rs.replace(old_finish, new_finish)
        changes.append('RevisionJob: max_revision_count=3 + rejection logic')
    
    rp.write_text(rs, encoding='utf-8')

p.write_text(s, encoding='utf-8')
print(f'OK: {", ".join(changes)}')