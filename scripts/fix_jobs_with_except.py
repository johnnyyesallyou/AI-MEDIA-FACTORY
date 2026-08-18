import re

files_to_fix = [
    '/app/backend/automation/jobs/revision_job.py',
    '/app/backend/automation/jobs/re_evaluation_job.py'
]

for file_path in files_to_fix:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        job_name = "RevisionJob" if "revision" in file_path else "ReEvaluationJob"
        
        # 1. Гарантированно добавляем execution_id (покрываем все варианты: с async, с типами, без типов)
        content = content.replace('def run(self, channel=None):', 'def run(self, channel=None, execution_id: str = None):')
        content = content.replace('def run(self, channel=None) -> dict:', 'def run(self, channel=None, execution_id: str = None) -> dict:')
        content = content.replace('def run(self, channel=None) -> dict[str, Any]:', 'def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:')
        content = content.replace('async def run(self, channel=None):', 'async def run(self, channel=None, execution_id: str = None):')
        content = content.replace('async def run(self, channel=None) -> dict:', 'async def run(self, channel=None, execution_id: str = None) -> dict:')
        content = content.replace('async def run(self, channel=None) -> dict[str, Any]:', 'async def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:')
        
        # 2. Добавляем инициализацию логгера сразу после строки с def run
        # Ищем строку с def run и добавляем после неё инициализацию
        pattern = rf'(def run\(self, channel=None, execution_id: str = None.*?\n)'
        replacement = r'\1        p_logger = PipelineLogger(execution_id, channel.id if channel else None)\n        p_logger.start("' + job_name.lower().replace('_job', '') + '")\n        try:\n'
        content = re.sub(pattern, replacement, content)
        
        # 3. Добавляем except блок перед return или в конец метода, чтобы ловить ошибки
        # Находим "finally:" или последний "return" и добавляем except перед ним
        if 'except Exception as e:' not in content:
            content = content.replace(
                '        finally:',
                '        except Exception as e:\n            error_msg = str(e)\n            logger.exception(f"{job_name} failed error=%s", error_msg)\n            p_logger.finish("failed", error_message=error_msg)\n            return {"status": "failed", "error": error_msg}\n\n        finally:'
            )
            
            # Если finally нет, добавляем except перед последним return
            if 'except Exception as e:' not in content:
                 content = content.replace(
                    '            return {',
                    '        except Exception as e:\n            error_msg = str(e)\n            logger.exception(f"{job_name} failed error=%s", error_msg)\n            p_logger.finish("failed", error_message=error_msg)\n            return {"status": "failed", "error": error_msg}\n\n            return {'
                )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ {file_path.split('/')[-1]} успешно обновлен с обработкой ошибок!")
    except Exception as e:
        print(f"❌ Ошибка при обработке {file_path}: {e}")
