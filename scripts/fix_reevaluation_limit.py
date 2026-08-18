import pathlib
p = pathlib.Path('./backend/automation/jobs/re_evaluation_job.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')

if 'items = repo.list_all(status="draft", limit=10)' in s:
    s = s.replace(
        'items = repo.list_all(status="draft", limit=10)',
        'items = repo.list_all(status="draft", limit=50)'
    )
    p.write_text(s, encoding='utf-8')
    print('OK: re_evaluation_job limit 10->50')
else:
    print('INFO: limit уже 50')