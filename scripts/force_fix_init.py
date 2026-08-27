import pathlib

p = pathlib.Path("/app/engines/telegraph/publisher.py")
lines = p.read_text(encoding="utf-8").split("\n")

# Ищем строку __init__ и добавляем self.access_token ПЕРЕД self.logger
new_lines = []
init_found = False
access_added = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Нашли строку с self.logger в __init__
    if "self.logger = logging.getLogger(self.__class__.__name__)" in line and not access_added:
        # Определяем отступ
        indent = len(line) - len(line.lstrip())
        indent_str = " " * indent
        
        # Вставляем self.access_token ПЕРЕД self.logger (удаляем последнюю добавленную строку и вставляем)
        new_lines.pop()  # удаляем self.logger
        
        # Вставляем access_token
        new_lines.append(f"{indent_str}self.access_token = access_token")
        new_lines.append(f'{indent_str}if not self.access_token:')
        new_lines.append(f'{indent_str}    import os')
        new_lines.append(f'{indent_str}    self.access_token = os.getenv("TELEGRAPH_ACCESS_TOKEN")')
        
        # Добавляем обратно self.logger
        new_lines.append(line)
        access_added = True
        print(f"[OK] Inserted self.access_token at line {i+1}")

if access_added:
    p.write_text("\n".join(new_lines), encoding="utf-8")
    print("[OK] __init__ restored with self.access_token")
else:
    print("[!] Could not find insertion point")
    # Ищем где self.logger
    for i, line in enumerate(lines):
        if "self.logger" in line:
            print(f"  Line {i+1}: {line.strip()}")