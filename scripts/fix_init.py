import pathlib, re

p = pathlib.Path("/app/engines/telegraph/publisher.py")
c = p.read_text(encoding="utf-8")

# Ищем сломанный __init__ с вложенным методом
# Паттерн: __init__ содержит def upload_images_to_telegraph внутри
if "def upload_images_to_telegraph" in c:
    # Извлекаем метод upload_images_to_telegraph
    start = c.find("    def upload_images_to_telegraph")
    if start != -1:
        # Находим конец метода (следующий def на том же уровне или конец)
        next_def = c.find("\n    def ", start + 10)
        if next_def == -1:
            next_def = len(c)
        
        method_code = c[start:next_def]
        
        # Удаляем метод из текущего места
        c = c[:start] + c[next_def:]
        
        # Вставляем метод ПЕРЕД create_account (на уровне класса)
        insert_pos = c.find("    def create_account")
        if insert_pos != -1:
            c = c[:insert_pos] + method_code + "\n" + c[insert_pos:]
            p.write_text(c, encoding="utf-8")
            print("[OK] upload_images_to_telegraph вынесен на уровень класса")
        else:
            print("[!] create_account not found")
    else:
        print("[!] method not found at class level")
else:
    print("[i] method not present")

# Проверяем что __init__ устанавливает access_token
c2 = p.read_text(encoding="utf-8")
init_start = c2.find("def __init__")
init_end = c2.find("def ", init_start + 10)
init_code = c2[init_start:init_end]
print(f"\n__init__ code:\n{init_code}")