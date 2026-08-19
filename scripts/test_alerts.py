import sys, os, json
sys.path.insert(0, "/app")

# Эмулируем падение Ollama и Telegram
os.environ["OLLAMA_URL"] = "http://localhost:9999"  # неправильный URL
os.environ["ALERT_BOT_TOKEN"] = sys.argv[1] if len(sys.argv) > 1 else ""
os.environ["ALERT_CHAT_ID"] = sys.argv[2] if len(sys.argv) > 2 else ""

from backend.automation.jobs.monitoring_job import MonitoringJob

print("=" * 60)
print("FIRST RUN - should send 2 alerts (ollama + telegram_api)")
print("=" * 60)
result1 = MonitoringJob().run()
print(json.dumps(result1, indent=2, ensure_ascii=False, default=str))

print("\n" + "=" * 60)
print("SECOND RUN - should suppress alerts (Redis dedup)")
print("=" * 60)
result2 = MonitoringJob().run()
print(json.dumps(result2, indent=2, ensure_ascii=False, default=str))

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"First run:  alerts_sent={result1['alerts_sent']}, suppressed={result1['alerts_suppressed']}")
print(f"Second run: alerts_sent={result2['alerts_sent']}, suppressed={result2['alerts_suppressed']}")
print("\nExpected:")
print("  First run:  alerts_sent=2 (ollama + telegram_api)")
print("  Second run: alerts_sent=0, suppressed=2 (dedup working)")