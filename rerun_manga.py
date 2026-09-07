import sys, asyncio
sys.path.insert(0, "/app")
from backend.automation.automation_manager_v2 import automation_manager_v2

async def main():
    await automation_manager_v2.start()
    result = await automation_manager_v2.run_channel_now("c0ddc7aa-ef76-4065-8791-d8f69530aebd")
    print(f"RESULT: {result}")
    await asyncio.sleep(90)
    print("=== DONE WAITING ===")

asyncio.run(main())