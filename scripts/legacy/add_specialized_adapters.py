import pathlib

p = pathlib.Path("/app/backend/automation/runtime/job_adapters.py")
c = p.read_text(encoding="utf-8")

# Добавляем импорты manga/anime jobs
imports_to_add = """
from backend.automation.jobs.manga_research_job import MangaResearchJob
from backend.automation.jobs.manga_enrichment_job import MangaEnrichmentJob
from backend.automation.jobs.manga_publish_job import MangaPublishJob
from backend.automation.jobs.anime_research_job import AnimeResearchJob
from backend.automation.jobs.anime_publish_job import AnimePublishJob
"""

# Ищем последнюю строку импорта
last_import_idx = c.rfind("from backend.automation.jobs")
if last_import_idx != -1:
    # Вставляем после последнего импорта jobs
    next_newline = c.find("\n", last_import_idx)
    c = c[:next_newline+1] + imports_to_add + c[next_newline+1:]
    print("[OK] Added manga/anime job imports")

# Добавляем адаптеры в конец файла
adapters = """

class MangaResearchJobAdapter(BaseJob):
    """Адаптер для MangaResearchJob."""
    node_type = "manga_research"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = MangaResearchJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            
            if isinstance(result, NodeResult):
                return result
            elif isinstance(result, dict):
                return NodeResult.success(result)
            else:
                return NodeResult.success({"result": result})
        except Exception as e:
            logger.error(f"MangaResearchJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class MangaEnrichmentJobAdapter(BaseJob):
    """Адаптер для MangaEnrichmentJob."""
    node_type = "manga_enrichment"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = MangaEnrichmentJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            
            if isinstance(result, NodeResult):
                return result
            elif isinstance(result, dict):
                return NodeResult.success(result)
            else:
                return NodeResult.success({"result": result})
        except Exception as e:
            logger.error(f"MangaEnrichmentJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class MangaPublishJobAdapter(BaseJob):
    """Адаптер для MangaPublishJob."""
    node_type = "manga_publish"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = MangaPublishJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            
            if isinstance(result, NodeResult):
                return result
            elif isinstance(result, dict):
                return NodeResult.success(result)
            else:
                return NodeResult.success({"result": result})
        except Exception as e:
            logger.error(f"MangaPublishJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class AnimeResearchJobAdapter(BaseJob):
    """Адаптер для AnimeResearchJob."""
    node_type = "anime_research"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = AnimeResearchJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            
            if isinstance(result, NodeResult):
                return result
            elif isinstance(result, dict):
                return NodeResult.success(result)
            else:
                return NodeResult.success({"result": result})
        except Exception as e:
            logger.error(f"AnimeResearchJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class AnimePublishJobAdapter(BaseJob):
    """Адаптер для AnimePublishJob."""
    node_type = "anime_publish"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = AnimePublishJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            
            if isinstance(result, NodeResult):
                return result
            elif isinstance(result, dict):
                return NodeResult.success(result)
            else:
                return NodeResult.success({"result": result})
        except Exception as e:
            logger.error(f"AnimePublishJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))
"""

if "class MangaResearchJobAdapter" not in c:
    c += adapters
    print("[OK] Added manga/anime adapters")

p.write_text(c, encoding="utf-8")