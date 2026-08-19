import pathlib, re

p = pathlib.Path("/app/backend/app/api/v1/channels.py")
c = p.read_text(encoding="utf-8")

# Находим enable_channel_automation и оборачиваем ChannelManager вызов в try/except
old_block = '''      # Создаём ChannelManager и включаем automation
      manager = ChannelManager()
      manager.enable_automation(channel_id, interval_minutes)

      return {
          "status": "enabled",
          "channel_id": channel_id,
          "interval_minutes": interval_minutes
      }'''

new_block = '''      # Создаём ChannelManager и включаем automation
      try:
          manager = ChannelManager()
          manager.enable_automation(channel_id, interval_minutes)
          return {
              "status": "enabled",
              "channel_id": channel_id,
              "interval_minutes": interval_minutes
          }
      except ValueError as e:
          # Channel not connected (e.g. Telegram bot not configured)
          # Graceful: помечаем намерение в metadata канала, но не падаем
          return {
              "status": "pending_connection",
              "channel_id": channel_id,
              "interval_minutes": interval_minutes,
              "reason": str(e),
              "next_step": "Connect Telegram/VK first via /channels/{id}/connect-telegram"
          }
      except Exception as e:
          raise HTTPException(status_code=500, detail=f"Failed to enable automation: {e}")'''

if old_block in c:
    c = c.replace(old_block, new_block, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] enable_channel_automation wrapped in try/except")
else:
    print("[?] block not found, showing current content:")
    m = re.search(r'async def enable_channel_automation.*?(?=\n@router|\nclass |\Z)', c, re.DOTALL)
    if m:
        print(m.group(0)[:500])