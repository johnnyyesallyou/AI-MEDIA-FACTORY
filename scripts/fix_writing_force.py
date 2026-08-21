import pathlib

p = pathlib.Path("/app/backend/automation/jobs/automation_jobs.py")
c = p.read_text(encoding="utf-8")

# Ищем точную строку 300
lines = c.split('\n')
for i, line in enumerate(lines):
    if 'return {"status": "ok", "items_processed": processed, "failed": failed}' in line:
        # Заменяем на conditional
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'status = "ok" if failed == 0 else "partial" if processed > 0 else "failed"'
        lines.insert(i+1, ' ' * indent + 'return {"status": status, "items_processed": processed, "failed": failed}')
        print(f"[OK] Fixed line {i+1}")
        break
    elif 'p_logger.finish("success", details=f"Processed {processed}, failed {failed}")' in line:
        # Заменяем PipelineLogger
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'logger_status = "success" if failed == 0 else "partial" if processed > 0 else "failed"'
        lines.insert(i+1, ' ' * indent + 'p_logger.finish(logger_status, details=f"Processed {processed}, failed {failed}")')
        print(f"[OK] Fixed PipelineLogger line {i+1}")
        break

c = '\n'.join(lines)
p.write_text(c, encoding="utf-8")
print("[OK] WritingJob fixed")