files_to_fix = [
    '/app/backend/automation/jobs/revision_job.py',
    '/app/backend/automation/jobs/re_evaluation_job.py'
]

for file_path in files_to_fix:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        job_name = "revision" if "revision" in file_path else "re_evaluation"
        new_lines = []
        in_run_method = False
        run_indent = 0
        
        for i, line in enumerate(lines):
            # 1. Находим начало метода run
            if 'def run(self, channel=None, execution_id: str = None)' in line:
                in_run_method = True
                run_indent = len(line) - len(line.lstrip())
                new_lines.append(line)
                # Добавляем инициализацию логгера и try
                new_lines.append(' ' * (run_indent + 4) + 'p_logger = PipelineLogger(execution_id, channel.id if channel else None)\n')
                new_lines.append(' ' * (run_indent + 4) + 'p_logger.start("' + job_name + '")\n')
                new_lines.append(' ' * (run_indent + 4) + 'try:\n')
                continue
            
            # 2. Если мы внутри метода run
            if in_run_method:
                current_indent = len(line) - len(line.lstrip())
                
                # Если встретили строку с таким же или меньшим отступом (и она не пустая), значит метод закончился
                if line.strip() and current_indent <= run_indent:
                    in_run_method = False
                    # Вставляем except блок ПЕРЕД концом метода
                    new_lines.append(' ' * (run_indent + 4) + 'except Exception as e:\n')
                    new_lines.append(' ' * (run_indent + 8) + 'error_msg = str(e)\n')
                    new_lines.append(' ' * (run_indent + 8) + 'logger.exception(f"Job failed error=%s", error_msg)\n')
                    new_lines.append(' ' * (run_indent + 8) + 'p_logger.finish("failed", error_message=error_msg)\n')
                    new_lines.append(' ' * (run_indent + 8) + 'return {"status": "failed", "error": error_msg}\n')
                    new_lines.append('\n')
            
            new_lines.append(line)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
        print(f"✅ {file_path.split('/')[-1]} успешно исправлен (построчно)!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
