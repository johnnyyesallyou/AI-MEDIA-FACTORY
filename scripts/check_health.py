import sys
sys.path.insert(0, '/app')

from backend.app.main import app

print("Registered routes:")
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', set())
        print(f"  {route.path} [{', '.join(methods)}]")