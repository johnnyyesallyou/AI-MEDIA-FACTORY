import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
content = p.read_text(encoding="utf-8")

# Ищем сломанную строку "description =" без продолжения
broken = '        description =\n'
if broken in content:
    print(f"Found broken line at position")
    fixed = '        description = metadata.get("manga_description", "")\n        # Sprint 19: только русские описания\n        if description and not re.search(r"[а-яА-ЯёЁ]", description):\n            description = ""\n'
    content = content.replace(broken, fixed, 1)
    p.write_text(content, encoding="utf-8")
    print("Fixed!")
else:
    print("Broken line not found, trying regex...")
    import re
    # Ищем любую строку "description =" за которой следует пустая строка или конец
    pattern = r'        description =\s*\n'
    matches = list(re.finditer(pattern, content))
    print(f"Found {len(matches)} matches for 'description ='")
    for i, m in enumerate(matches):
        print(f"  {i}: pos {m.start()} -> {repr(m.group()[:40])}")
    
    if matches:
        fixed = '        description = metadata.get("manga_description", "")\n        # Sprint 19: только русские описания\n        if description and not re.search(r"[а-яА-ЯёЁ]", description):\n            description = ""\n'
        # Заменяем все найденные сломанные строки
        new_content = re.sub(pattern, fixed, content)
        p.write_text(new_content, encoding="utf-8")
        print("Fixed via regex!")

# Проверяем синтаксис
import ast
try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("Syntax OK")
except SyntaxError as e:
    print(f"Syntax error still present: {e}")
    # Показываем проблемный участок
    lines = p.read_text(encoding="utf-8").splitlines()
    line_no = e.lineno
    for i in range(max(0, line_no-5), min(len(lines), line_no+5)):
        marker = ">>>" if i+1 == line_no else "   "
        print(f"{marker} {i+1:3}: {lines[i]}")