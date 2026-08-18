import sys
import json
sys.path.insert(0, "/app")

from core.channel_manager import ChannelManager

print("=" * 70)
print("TEST: Channel Manager")
print("=" * 70)

manager = ChannelManager()

print("\n[1] List all channels:")
channels = manager.list_channels()
for ch in channels[:3]:
    print(f"  {ch['name']} ({ch['platform']}): connected={ch['is_connected']}")

print(f"\n  Total: {len(channels)} channels")

print("\n[2] Get status:")
status = manager.get_status()
print(json.dumps(status, indent=2, default=str))

print("\n" + "=" * 70)
print("CHANNEL MANAGER TEST PASSED ✅")
print("=" * 70)