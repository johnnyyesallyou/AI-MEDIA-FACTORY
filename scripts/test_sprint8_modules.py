import sys
sys.path.insert(0, '.')

print("=" * 80)
print("Тест 1: Импорт policies.py")
print("=" * 80)
try:
    from backend.automation.policies import RetryPolicy, RateLimitPolicy, ErrorHandlingPolicy
    print("✅ Import successful")
    
    # Test RetryPolicy
    retry_policy = RetryPolicy(max_retries=3, backoff_factor=2.0, base_delay=5.0)
    print(f"\nRetryPolicy:")
    print(f"  should_retry(0, 3) = {retry_policy.should_retry(0, 3)}")  # True
    print(f"  should_retry(3, 3) = {retry_policy.should_retry(3, 3)}")  # False
    print(f"  get_backoff_time(0) = {retry_policy.get_backoff_time(0)}s")  # 5.0
    print(f"  get_backoff_time(1) = {retry_policy.get_backoff_time(1)}s")  # 10.0
    print(f"  get_backoff_time(2) = {retry_policy.get_backoff_time(2)}s")  # 20.0
    
    # Test ErrorHandlingPolicy
    error_policy = ErrorHandlingPolicy()
    print(f"\nErrorHandlingPolicy:")
    print(f"  log_errors = {error_policy.log_errors}")
    print(f"  notify_on_failure = {error_policy.notify_on_failure}")
    print(f"  auto_recover = {error_policy.auto_recover}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Тест 2: Импорт workflow.py")
print("=" * 80)
try:
    from backend.automation.workflow import (
        WorkflowDefinition, 
        WorkflowStage, 
        WorkflowStageType
    )
    print("✅ Import successful")
    
    # Test default workflow
    default_wf = WorkflowDefinition.default()
    print(f"\nDefault workflow:")
    print(f"  name: {default_wf.name}")
    print(f"  stages: {default_wf.get_stage_names()}")
    
    # Test simple workflow
    simple_wf = WorkflowDefinition.simple()
    print(f"\nSimple workflow:")
    print(f"  name: {simple_wf.name}")
    print(f"  stages: {simple_wf.get_stage_names()}")
    
    # Test from_config
    config = {
        "name": "custom_test",
        "description": "Custom workflow",
        "stages": [
            {"stage_type": "research", "enabled": True},
            {"stage_type": "writing", "enabled": True},
            {"stage_type": "publish", "enabled": False},
        ]
    }
    custom_wf = WorkflowDefinition.from_config(config)
    print(f"\nCustom workflow from config:")
    print(f"  name: {custom_wf.name}")
    print(f"  all stages: {[s.stage_type.value for s in custom_wf.stages]}")
    print(f"  enabled stages: {custom_wf.get_stage_names()}")
    
    # Test to_config round-trip
    roundtrip_config = custom_wf.to_config()
    print(f"\nRound-trip to_config:")
    print(f"  stages: {roundtrip_config['stages']}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ Все тесты завершены!")
print("=" * 80)