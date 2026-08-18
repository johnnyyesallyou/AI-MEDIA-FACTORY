import re, pathlib
root = pathlib.Path('./frontend/src')
pat = re.compile(r'([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)+)\.substring\(')
for p in list(root.rglob('*.tsx')) + list(root.rglob('*.ts')):
    s = p.read_text(encoding='utf-8')
    new = pat.sub(lambda m: '({} || "").substring('.format(m.group(1)), s)
    if new != s:
        p.write_text(new, encoding='utf-8')
        print('✅ Patched:', p)