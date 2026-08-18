import pathlib

p = pathlib.Path('./backend/automation/jobs/revision_job.py')
s = p.read_text(encoding='utf-8-sig').replace('\ufeff', '')

# Заменяем все использования MAX_REVISION_COUNT на self.MAX_REVISION_COUNT
# (но не трогаем определение константы)
lines = s.split('\n')
new_lines = []
for line in lines:
    # Пропускаем строку с определением константы
    if 'MAX_REVISION_COUNT = 3' in line:
        new_lines.append(line)
        continue
    
    # Заменяем все остальные использования
    if 'MAX_REVISION_COUNT' in line and 'self.MAX_REVISION_COUNT' not in line:
        line = line.replace('MAX_REVISION_COUNT', 'self.MAX_REVISION_COUNT')
    
    new_lines.append(line)

s = '\n'.join(new_lines)
p.write_text(s, encoding='utf-8')
print('OK: все MAX_REVISION_COUNT заменены на self.MAX_REVISION_COUNT')