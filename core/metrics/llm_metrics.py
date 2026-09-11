"""Sprint 73.3: LLM metrics collection (end-to-end per pipeline run)."""
import contextvars
from dataclasses import dataclass, field


@dataclass
class LLMMetricsCollector:
    """Агрегирует LLM-метрики за один прогон pipeline.

    Заполняется автоматически из вызовов Ollama (llm_post_generator),
    живёт в ContextVar → переживает await-цепочки внутри одной задачи,
    не путается между параллельными каналами (семафор 3).
    """

    llm_calls: int = 0
    llm_errors: int = 0
    llm_latency_ms: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    llm_model: str = ""
    per_call: list = field(default_factory=list)

    def record_call(
        self,
        latency_ms: int,
        tokens_in: int = 0,
        tokens_out: int = 0,
        model: str = "",
    ) -> None:
        self.llm_calls += 1
        self.llm_latency_ms += latency_ms
        self.tokens_in += tokens_in
        self.tokens_out += tokens_out
        if model:
            self.llm_model = model
        self.per_call.append({
            "latency_ms": latency_ms,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "model": model,
        })

    def record_error(self) -> None:
        self.llm_errors += 1

    @property
    def avg_latency_ms(self) -> int:
        return int(self.llm_latency_ms / self.llm_calls) if self.llm_calls else 0

    def to_dict(self) -> dict:
        return {
            "llm_calls": self.llm_calls,
            "llm_errors": self.llm_errors,
            "llm_latency_ms": self.llm_latency_ms,
            "llm_avg_latency_ms": self.avg_latency_ms,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "llm_model": self.llm_model,
        }


_current_collector: contextvars.ContextVar = contextvars.ContextVar(
    "llm_metrics_collector", default=None
)


def start_llm_collection() -> LLMMetricsCollector:
    """Начать сбор LLM-метрик для текущего контекста (вызывается в pipeline.run)."""
    collector = LLMMetricsCollector()
    _current_collector.set(collector)
    return collector


def get_llm_collector() -> LLMMetricsCollector:
    """Получить активный коллектор (или создать пустой — безопасно вне pipeline)."""
    collector = _current_collector.get()
    if collector is None:
        collector = LLMMetricsCollector()
        _current_collector.set(collector)
    return collector