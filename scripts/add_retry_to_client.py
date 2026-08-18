import pathlib
p = pathlib.Path('./frontend/src/api/client.ts')
c = p.read_text(encoding='utf-8')

if 'retry: (' not in c:
    c = c.replace(
        "  runNow: () => apiClient.post('/automation/run-now'),",
        "  runNow: () => apiClient.post('/automation/run-now'),\n  retry: (execution_id: string, stage: string) => apiClient.post('/automation/retry', { execution_id, stage }),"
    )
    p.write_text(c, encoding='utf-8')
    print('OK: retry added to automationAPI')