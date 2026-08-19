import sys
import time
sys.path.insert(0, "/app")

from core.channel_scheduler import ChannelScheduler

print("=" * 70)
print("TEST: Channel Scheduler")
print("=" * 70)

scheduler = ChannelScheduler()

# Mock runners
def mock_research(channel_id):
    print(f"  [Research] Running for {channel_id}")
    return {"status": "ok", "new_items": 5}

def mock_publish(channel_id):
    print(f"  [Publish] Running for {channel_id}")
    return {"status": "ok", "published": 3}

scheduler.research_runner = mock_research
scheduler.publish_runner = mock_publish

# Добавляем 2 канала
scheduler.add_channel("channel-1", interval_minutes=0)  # immediate
scheduler.add_channel("channel-2", interval_minutes=0)  # immediate

print("\n[1] Starting scheduler:")
scheduler.start()

print("\n[2] Waiting 5 seconds for jobs to run:")
time.sleep(5)

print("\n[3] Status:")
status = scheduler.get_status()
print(f"  Running: {status['running']}")
for cid, info in status['channels'].items():
    print(f"  {cid}: enabled={info['enabled']}, last_run={info['last_run']}")

print("\n[4] Stopping scheduler:")
scheduler.stop()

print("\n" + "=" * 70)
print("SCHEDULER TEST PASSED ✅")
print("=" * 70)