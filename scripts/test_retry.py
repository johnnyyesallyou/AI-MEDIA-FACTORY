import sys
sys.path.insert(0, "/app")

from core.retry import retry_on_failure
import time

print("=" * 70)
print("TEST: Retry decorator")
print("=" * 70)

# Test 1: Success на 3-й попытке
call_count = 0

@retry_on_failure(max_retries=3, backoff_factor=1.0, exceptions=(ValueError,))
def flaky_function():
    global call_count
    call_count += 1
    print(f"  Attempt {call_count}")
    if call_count < 3:
        raise ValueError(f"Simulated failure {call_count}")
    return "Success!"

print("\n[1] Retry until success:")
result = flaky_function()
print(f"  Result: {result}")
print(f"  Total calls: {call_count}")
assert call_count == 3, "Should retry 3 times"

# Test 2: Final failure
call_count_2 = 0

@retry_on_failure(max_retries=2, backoff_factor=1.0, exceptions=(ValueError,))
def always_fail():
    global call_count_2
    call_count_2 += 1
    raise ValueError("Always fails")

print("\n[2] Final failure after max retries:")
try:
    always_fail()
    print("  ❌ Should have raised exception")
except ValueError as e:
    print(f"  ✅ Exception raised after {call_count_2} attempts: {e}")
    assert call_count_2 == 2

print("\n" + "=" * 70)
print("RETRY TESTS PASSED ✅")
print("=" * 70)