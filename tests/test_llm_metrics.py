"""Sprint 73.3: Tests for LLM metrics collection."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.metrics.llm_metrics import (
    LLMMetricsCollector,
    start_llm_collection,
    get_llm_collector,
)


class TestLLMMetricsCollector:
    def test_record_call_accumulates(self):
        c = LLMMetricsCollector()
        c.record_call(latency_ms=100, tokens_in=50, tokens_out=30, model="llama3.1:8b")
        c.record_call(latency_ms=200, tokens_in=60, tokens_out=40, model="llama3.1:8b")
        assert c.llm_calls == 2
        assert c.llm_latency_ms == 300
        assert c.tokens_in == 110
        assert c.tokens_out == 70
        assert c.llm_model == "llama3.1:8b"
        assert c.avg_latency_ms == 150

    def test_record_error(self):
        c = LLMMetricsCollector()
        c.record_error()
        c.record_error()
        assert c.llm_errors == 2
        assert c.llm_calls == 0
        assert c.avg_latency_ms == 0

    def test_to_dict(self):
        c = LLMMetricsCollector()
        c.record_call(latency_ms=80, tokens_in=10, tokens_out=5, model="test")
        d = c.to_dict()
        assert d["llm_calls"] == 1
        assert d["llm_latency_ms"] == 80
        assert d["llm_avg_latency_ms"] == 80
        assert d["tokens_in"] == 10
        assert d["tokens_out"] == 5
        assert d["llm_model"] == "test"

    def test_contextvar_isolation_across_tasks(self):
        """Параллельные каналы не должны смешивать метрики."""
        async def worker(n):
            collector = start_llm_collection()
            collector.record_call(latency_ms=n, model="m")
            await asyncio.sleep(0.01)  # имитация LLM-вызова
            c = get_llm_collector()
            assert c is collector
            c.record_call(latency_ms=n, model="m")
            return c.to_dict()

        async def main():
            return await asyncio.gather(worker(111), worker(222))

        d1, d2 = asyncio.run(main())
        assert d1["llm_calls"] == 2 and d1["llm_latency_ms"] == 222
        assert d2["llm_calls"] == 2 and d2["llm_latency_ms"] == 444


class TestPipelineExecutionId:
    def test_pipeline_result_has_execution_id(self):
        from backend.engines.universal_pipeline import PipelineResult
        r = PipelineResult(success=True)
        r.execution_id = "20260909-120000-abcdef12"
        assert r.execution_id == "20260909-120000-abcdef12"
        assert r.llm_metrics == {}


if __name__ == "__main__":
    raise SystemExit("Run with pytest")
