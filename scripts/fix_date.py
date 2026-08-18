import pathlib
p = pathlib.Path('./frontend/src/pages/Logs.tsx')
s = p.read_text(encoding='utf-8')
old = "setLogs(response.data.items || []);"
new = "setLogs((response.data.items || []).map((l: any) => ({ ...l, timestamp: l.created_at || l.timestamp })));"
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')
    print("✅ Logs.tsx: created_at -> timestamp, Invalid Date исправлен!")
else:
    print("⚠️ Строка не найдена — покажем, что там:")
    import re
    for i, line in enumerate(s.splitlines(), 1):
        if "setLogs" in line: print(i, line)