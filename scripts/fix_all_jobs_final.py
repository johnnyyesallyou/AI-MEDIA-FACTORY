file_path = '/app/backend/automation/jobs/automation_jobs.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Гарантированно обновляем DecisionJob
content = content.replace(
    'class DecisionJob:\n\n    def run(self, channel=None) -> dict[str, Any]:',
    'class DecisionJob:\n\n    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:\n        p_logger = PipelineLogger(execution_id, channel.id if channel else None)\n        p_logger.start("decision")'
)

# 2. Гарантированно обновляем RevisionJob
content = content.replace(
    'class RevisionJob:\n\n    def run(self, channel=None) -> dict[str, Any]:',
    'class RevisionJob:\n\n    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:\n        p_logger = PipelineLogger(execution_id, channel.id if channel else None)\n        p_logger.start("revision")'
)

# 3. Гарантированно обновляем ReEvaluationJob
content = content.replace(
    'class ReEvaluationJob:\n\n    def run(self, channel=None) -> dict[str, Any]:',
    'class ReEvaluationJob:\n\n    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:\n        p_logger = PipelineLogger(execution_id, channel.id if channel else None)\n        p_logger.start("re_evaluation")'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Все джобы (включая Decision, Revision, ReEvaluation) гарантированно обновлены!')
