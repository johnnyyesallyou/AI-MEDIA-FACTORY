import re

file_path = '/app/backend/automation/jobs/automation_jobs.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Обновляем WritingJob
content = content.replace(
    'class WritingJob:\n\n    def run(self, channel=None) -> dict[str, Any]:\n\n        logger.info("WritingJob started")',
    'class WritingJob:\n\n    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:\n        p_logger = PipelineLogger(execution_id, channel.id if channel else None)\n        p_logger.start("writing")\n\n        logger.info("WritingJob started")'
)
content = content.replace(
    'failed = 0\n\n\n        return {',
    'failed = 0\n        p_logger.finish("success", details=f"Processed {processed}, failed {failed}")\n\n\n        return {'
)

# 2. Обновляем EvaluatorJob
content = content.replace(
    'class EvaluatorJob:\n\n    async def run(self, channel=None) -> dict[str, Any]:\n\n        logger.info(\n            "EvaluatorJob started"\n        )',
    'class EvaluatorJob:\n\n    async def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:\n        p_logger = PipelineLogger(execution_id, channel.id if channel else None)\n        p_logger.start("evaluation")\n\n        logger.info(\n            "EvaluatorJob started"\n        )'
)
content = content.replace(
    'approved = 0\n\n\n        return {',
    'approved = 0\n        p_logger.finish("success", details=f"Processed {processed}, approved {approved}")\n\n\n        return {'
)

# 3. Обновляем PublishJob
content = content.replace(
    'class PublishJob:\n\n    def run(self, channel=None) -> dict[str, Any]:\n\n        logger.info("PublishJob started")',
    'class PublishJob:\n\n    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:\n        p_logger = PipelineLogger(execution_id, channel.id if channel else None)\n        p_logger.start("publish")\n\n        logger.info("PublishJob started")'
)
content = content.replace(
    'failed = 0\n\n        try:',
    'failed = 0\n\n        try:\n            p_logger.finish("success", details=f"Published {published}, failed {failed}")'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Все джобы успешно обновлены с логированием!')
