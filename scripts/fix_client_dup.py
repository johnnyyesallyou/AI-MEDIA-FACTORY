import re, pathlib
p = pathlib.Path('./frontend/src/api/client.ts')
c = p.read_text(encoding='utf-8')
dup = "\n\n// Automation API\nexport const automationAPI = {\n  getSchedulerStatus: () => apiClient.get('/automation/scheduler/status'),\n};"
if dup in c:
    c = c.replace(dup, '')
    print('OK: duplicate removed')
if 'getSchedulerStatus' not in c:
    c2 = re.sub(r'(export const automationAPI\s*=\s*\{)', r"\1`n  getSchedulerStatus: () => apiClient.get('/automation/scheduler/status'),".replace('`n','\n'), c, count=1)
    if c2 != c:
        c = c2
        print('OK: getSchedulerStatus added to existing automationAPI')
    else:
        print('ERROR: automationAPI not found')
p.write_text(c, encoding='utf-8')