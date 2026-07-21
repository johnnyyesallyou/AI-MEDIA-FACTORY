from .model_routing import ModelRoutingConfig, ModelConfig, TaskRoutingRule, LLMProvider

def get_default_routing_config() -> ModelRoutingConfig:
    '''
    Возвращает конфигурацию роутинга по умолчанию.
    В будущем это будет загружаться из БД или config.yaml.
    '''
    return ModelRoutingConfig(
        available_models={
            "qwen3-32b": ModelConfig(
                id="qwen3-32b",
                provider=LLMProvider.QWEN,
                model_name="qwen3-32b",
                context_window=32768,
                max_output_tokens=4096,
                api_key_env_var="QWEN_API_KEY"
            ),
            "gpt-oss": ModelConfig(
                id="gpt-oss",
                provider=LLMProvider.OPENAI, # или OLLAMA, если локальный
                model_name="gpt-4o-mini", # пример OSS-совместимой или легкой модели
                context_window=8192,
                max_output_tokens=2048,
                api_key_env_var="OPENAI_API_KEY"
            ),
            "gemma-27b": ModelConfig(
                id="gemma-27b",
                provider=LLMProvider.GEMMA,
                model_name="gemma-2-27b-it",
                context_window=8192,
                max_output_tokens=2048,
                api_key_env_var="GEMMA_API_KEY"
            ),
            "deepseek-chat": ModelConfig(
                id="deepseek-chat",
                provider=LLMProvider.DEEPSEEK,
                model_name="deepseek-chat",
                context_window=32768,
                max_output_tokens=4096,
                api_key_env_var="DEEPSEEK_API_KEY"
            )
        },
        task_rules={
            "research": TaskRoutingRule(
                task_name="research",
                primary_model_id="gpt-oss",
                fallback_model_id="deepseek-chat",
                temperature=0.2, # Низкая температура для точного извлечения фактов
                top_p=0.9
            ),
            "writing": TaskRoutingRule(
                task_name="writing",
                primary_model_id="qwen3-32b",
                fallback_model_id="gpt-oss",
                temperature=0.7, # Средняя температура для креативности в рамках фактов
                top_p=0.9
            ),
            "fact_check": TaskRoutingRule(
                task_name="fact_check",
                primary_model_id="gemma-27b",
                fallback_model_id="qwen3-32b",
                temperature=0.1, # Очень низкая температура для строгой логики
                top_p=0.5
            ),
            "evaluator": TaskRoutingRule(
                task_name="evaluator",
                primary_model_id="deepseek-chat",
                fallback_model_id="gemma-27b",
                temperature=0.3, # Низкая температура для объективной оценки
                top_p=0.8
            )
        }
    )
