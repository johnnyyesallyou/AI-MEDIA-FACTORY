from typing import Dict
from .models import ABTestConfig, ABTestResult, PromptVariant, TestStatus
from datetime import datetime

class PromptLabEngine:
    '''
    Движок для управления A/B тестами промптов.
    В будущем будет использовать PostgreSQL для хранения данных.
    '''
    
    def __init__(self):
        # In-memory хранилища для демонстрации
        self._variants: Dict[str, PromptVariant] = {}
        self._tests: Dict[str, ABTestConfig] = {}
        self._results: Dict[str, ABTestResult] = {}
        
        # Агрегаторы метрик: test_id -> {variant_id: total_score}
        self._metrics_sum: Dict[str, Dict[str, float]] = {} 
        # Счетчики показов: test_id -> {variant_id: count}
        self._metrics_count: Dict[str, Dict[str, int]] = {} 

    def register_variant(self, variant: PromptVariant):
        '''Регистрирует новый вариант промпта в системе.'''
        self._variants[variant.id] = variant

    def create_test(self, config: ABTestConfig):
        '''Создает и запускает новый A/B тест.'''
        if config.variant_a_id not in self._variants or config.variant_b_id not in self._variants:
            raise ValueError('Один из вариантов промпта не зарегистрирован.')
        
        self._tests[config.id] = config
        config.status = TestStatus.RUNNING
        
        # Инициализируем счетчики
        self._metrics_sum[config.id] = {config.variant_a_id: 0.0, config.variant_b_id: 0.0}
        self._metrics_count[config.id] = {config.variant_a_id: 0, config.variant_b_id: 0}

    def record_metric(self, test_id: str, variant_id: str, value: float):
        '''
        Записывает метрику (например, CTR) для конкретного варианта в рамках теста.
        Вызывается, когда пост опубликован и получена аналитика.
        '''
        if test_id not in self._metrics_sum or variant_id not in self._metrics_sum[test_id]:
            return
            
        self._metrics_sum[test_id][variant_id] += value
        self._metrics_count[test_id][variant_id] += 1

    def calculate_winner(self, test_id: str) -> ABTestResult:
        '''
        Анализирует накопленные метрики и определяет победителя.
        '''
        config = self._tests.get(test_id)
        if not config:
            raise ValueError('Тест не найден.')

        # Считаем средние значения
        avg_a = self._metrics_sum[test_id][config.variant_a_id] / max(1, self._metrics_count[test_id][config.variant_a_id])
        avg_b = self._metrics_sum[test_id][config.variant_b_id] / max(1, self._metrics_count[test_id][config.variant_b_id])

        # Определяем победителя
        winner_id = config.variant_a_id if avg_a >= avg_b else config.variant_b_id
        
        # Упрощенный расчет уверенности (в реальности нужен статистический тест, например, t-test)
        total_samples = self._metrics_count[test_id][config.variant_a_id] + self._metrics_count[test_id][config.variant_b_id]
        confidence = min(1.0, total_samples / 100.0) 

        result = ABTestResult(
            id=f'res_{test_id}',
            test_id=test_id,
            variant_a_avg_score=avg_a,
            variant_b_avg_score=avg_b,
            winning_variant_id=winner_id,
            confidence=confidence,
            completed_at=datetime.utcnow()
        )
        
        config.status = TestStatus.COMPLETED
        self._results[test_id] = result
        return result
