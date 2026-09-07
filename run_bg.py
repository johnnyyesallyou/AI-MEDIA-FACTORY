import sys, asyncio
sys.path.insert(0, "/app")
from backend.automation.automation_manager_v2 import automation_manager_v2

async def main():
    await automation_manager_v2.start()
    result = await automation_manager_v2.run_channel_now("e4902a88-e163-40af-82b0-08dc2126fd22")
    print(f"RESULT: {result}", flush=True)
    await asyncio.sleep(600)  # ждём до 10 минут

asyncio.run(main())