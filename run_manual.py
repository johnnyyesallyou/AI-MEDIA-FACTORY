import sys
import asyncio
sys.path.insert(0, "/app")
from backend.automation.automation_manager_v2 import automation_manager_v2

async def main():
    await automation_manager_v2.start()
    print("\nЗапускаю AI News Daily вручную...")
    result = await automation_manager_v2.run_channel_now("1443b761-5fb4-44ed-82ae-78cccf6d2bef")
    print(f"Result: {result}")
    
    # Ждём завершения (до 10 минут)
    print("Жду завершения pipeline (до 10 минут)...")
    await asyncio.sleep(600)

asyncio.run(main())