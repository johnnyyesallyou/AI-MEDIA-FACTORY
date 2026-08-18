import pathlib

p = pathlib.Path('./backend/automation/jobs/revision_job.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')

# Добавляем константу в начало класса RevisionJob
old_block = '''class RevisionJob:

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:'''

new_block = '''class RevisionJob:
    MAX_REVISION_COUNT = 3  # Защита от бесконечного цикла

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:'''

if old_block in s and 'MAX_REVISION_COUNT' not in s:
    s = s.replace(old_block, new_block)
    # Также нужно использовать self.MAX_REVISION_COUNT или RevisionJob.MAX_REVISION_COUNT
    s = s.replace('if current_count >= MAX_REVISION_COUNT:', 'if current_count >= self.MAX_REVISION_COUNT:')
    s = s.replace('({MAX_REVISION_COUNT})', '({self.MAX_REVISION_COUNT})')
    p.write_text(s, encoding='utf-8')
    print('OK: MAX_REVISION_COUNT added to RevisionJob')
else:
    print('INFO: already has MAX_REVISION_COUNT or pattern not found')