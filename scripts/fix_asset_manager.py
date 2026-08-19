import pathlib, py_compile

f = pathlib.Path('./engines/asset/manager.py')
s = f.read_text(encoding='utf-8')

# Ищем блок где сохраняем файл и добавляем валидацию
old_save = '''            # Сохраняем файл
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            generation_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            file_size = file_path.stat().st_size'''

new_save = '''            # Сохраняем файл
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            generation_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            file_size = file_path.stat().st_size
            
            # Валидация: файл не должен быть пустым
            if file_size == 0:
                logger.error(f"Downloaded file is empty (0 bytes)")
                file_path.unlink()  # Удаляем пустой файл
                raise ValueError("Downloaded file is empty (0 bytes)")
            
            # Валидация: минимальный размер для изображения (1KB)
            if file_size < 1024:
                logger.warning(f"File too small ({file_size} bytes), might be corrupted")'''

if old_save in s:
    s = s.replace(old_save, new_save, 1)
    f.write_text(s, encoding='utf-8')
    print("✅ AssetManager обновлён — валидация размера файла")
else:
    print("⚠️ Паттерн не найден")

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ manager.py валиден! ✅✅✅")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")