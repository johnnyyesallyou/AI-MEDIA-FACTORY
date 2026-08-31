import pathlib

# Функция для удаления всех BOM-символов
def clean_bom(file_path):
    p = pathlib.Path(file_path)
    if not p.exists():
        return False
    # Читаем как utf-8-sig (убирает BOM в начале) + удаляем оставшиеся \ufeff
    s = p.read_text(encoding='utf-8-sig')
    s = s.replace('\ufeff', '')  # Удаляем все оставшиеся BOM-символы
    p.write_text(s, encoding='utf-8')  # Записываем без BOM
    return True

# Чистим оба файла
if clean_bom('./engines/writing/engine.py'):
    print('OK: engines/writing/engine.py cleaned')
if clean_bom('./backend/app/api/v1/ai.py'):
    print('OK: backend/app/api/v1/ai.py cleaned')