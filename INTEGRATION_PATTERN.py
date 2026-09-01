"""
Sprint 66.5.5: Integration example - How to add ErrorLogger to existing jobs

This shows the pattern for integrating error tracking into automation workers.
Add this pattern to: news_research_job.py, anime_research_job.py, etc.
"""

# BEFORE (existing code):
"""
def run(self, channel, limit_per_source=20):
    try:
        result = fetch_data()
        return {"status": "ok", "data": result}
    except Exception as e:
        logger.exception(f"Failed: {e}")
        return {"status": "failed", "error": str(e)}
"""

# AFTER (with error tracking):
"""
from backend.core.error_logger import get_error_logger

def run(self, channel, limit_per_source=20, execution_id=None):
    error_logger = get_error_logger()
    
    try:
        result = fetch_data()
        return {"status": "ok", "data": result, "execution_id": execution_id}
    except TimeoutError as e:
        error_logger.log_timeout(
            channel_id=channel.id,
            pipeline="research",
            job="fetch_data",
            timeout_seconds=30.0,
            execution_id=execution_id,
        )
        logger.exception(f"Timeout: {e}")
        return {"status": "failed", "error": str(e), "execution_id": execution_id}
    except Exception as e:
        error_logger.log_exception(
            channel_id=channel.id,
            pipeline="research",
            job="fetch_data",
            exception=e,
            execution_id=execution_id,
        )
        logger.exception(f"Failed: {e}")
        return {"status": "failed", "error": str(e), "execution_id": execution_id}
"""

# KEY CHANGES:
# 1. Import: from backend.core.error_logger import get_error_logger
# 2. Add execution_id parameter to run()
# 3. Create error_logger instance
# 4. Call log_timeout() for TimeoutError
# 5. Call log_exception() for other exceptions
# 6. Return execution_id in response

print(__doc__)
