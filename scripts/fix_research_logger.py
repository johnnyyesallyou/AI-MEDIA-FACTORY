import pathlib, re

p = pathlib.Path('./backend/automation/jobs/automation_jobs.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')

# Ищем ранний p_logger.finish в ResearchJob и переносим в конец
# Текущий паттерн:
old_pattern = r'''        created = 0
        skipped = 0
        p_logger\.finish\("success", details=f"Created \{created\}, skipped \{skipped\}"\)

        try:'''

new_pattern = '''        created = 0
        skipped = 0

        try:'''

s_new = re.sub(old_pattern, new_pattern, s)

# Теперь добавляем p_logger.finish в самом конце try-блока (после db.close())
# Ищем финальное "finally: db.close()" или "return" в ResearchJob

# Более точный подход: найдём "return {" в ResearchJob.run и добавим перед ним
# Сначала найдём класс ResearchJob
class_start = s_new.find('class ResearchJob:')
class_end = s_new.find('\nclass ', class_start + 1)
if class_end == -1:
    class_end = len(s_new)

research_job = s_new[class_start:class_end]

# Ищем последний return в ResearchJob
# Паттерн: return { ... "status": ... }
return_pattern = r'(\s+)return \{\s*"status"'
matches = list(re.finditer(return_pattern, research_job))
if matches:
    last_match = matches[-1]
    indent = last_match.group(1)
    
    insert_text = f'''{indent}p_logger.finish("success", details=f"Created {{created}}, skipped {{skipped}}")
'''
    
    # Вставляем перед последним return
    pos = class_start + last_match.start()
    s_new = s_new[:pos] + insert_text + s_new[pos:]
    print('OK: p_logger.finish moved to end of ResearchJob')
else:
    print('WARN: return pattern not found')

p.write_text(s_new, encoding='utf-8')
print('DONE')