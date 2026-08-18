import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

# Добавляем проверку размера файла перед отправкой
old_check = '''            if not image_url:
                return {"status": "failed", "error": "No image URL"}'''

new_check = '''            if not image_url:
                return {"status": "failed", "error": "No image URL"}
            
            # Sprint 19: Проверяем что файл существует и не пустой (для локальных файлов)
            if image_url.startswith("/assets/"):
                file_path = f"/app{image_url}" if not image_url.startswith("/app") else image_url
                if not pathlib.Path(file_path).exists() or pathlib.Path(file_path).stat().st_size == 0:
                    self.logger.error(f"File not found or empty: {file_path}")
                    return {"status": "failed", "error": "File not found or empty"}'''

if old_check in c:
    c = c.replace(old_check, new_check)
    print("✅ Added file existence check")
else:
    print("❌ Block not found")

p.write_text(c, encoding="utf-8")
import ast
ast.parse(c)
print("✅ Syntax OK")