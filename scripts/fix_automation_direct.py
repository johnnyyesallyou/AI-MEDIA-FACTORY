import pathlib, re

p = pathlib.Path('/app/backend/app/api/v1/channels.py')
c = p.read_text(encoding='utf-8')

# Ищем блок enable_channel_automation
pattern = r'(async def enable_channel_automation\(.*?\n    """.*?"""\n.*?)manager = ChannelManager\(\)\s+manager\.enable_automation\(channel_id, interval_minutes\)\s+return \{[^}]+\}'

def replace_func(match):
    before = match.group(1)
    return before + '''try:
        manager = ChannelManager()
        manager.enable_automation(channel_id, interval_minutes)
        return {
            "status": "enabled",
            "channel_id": channel_id,
            "interval_minutes": interval_minutes
        }
    except ValueError as e:
        # Channel not connected
        return {
            "status": "pending_connection",
            "channel_id": channel_id,
            "interval_minutes": interval_minutes,
            "reason": str(e),
            "next_step": "Connect Telegram first via /channels/{id}/connect-telegram"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automation error: {e}")'''

c_new = re.sub(pattern, replace_func, c, flags=re.DOTALL)

if c_new != c:
    p.write_text(c_new, encoding='utf-8')
    print("  ✅ try/except применён")
else:
    print("  ? Паттерн не найден или уже применён")