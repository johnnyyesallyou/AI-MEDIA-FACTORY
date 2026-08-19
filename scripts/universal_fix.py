import pathlib
import yaml
import sys

# 1. Найти main.py
main_candidates = [
    "/app/backend/main.py",
    "/app/backend/app/main.py", 
    "/app/main.py",
]

main_path = None
for p in main_candidates:
    if pathlib.Path(p).exists():
        main_path = p
        break

if not main_path:
    # Поиск через glob
    import glob
    found = glob.glob("/app/**/main.py", recursive=True)
    if found:
        main_path = found[0]

print(f"main.py found at: {main_path}")

if main_path:
    c = pathlib.Path(main_path).read_text(encoding="utf-8")
    
    # Определяем правильный import path из существующих imports
    if "from backend.app.api.v1" in c:
        metrics_import = "from backend.app.api.v1 import metrics"
        router_register = "app.include_router(metrics.router)"
    elif "from app.api.v1" in c:
        metrics_import = "from app.api.v1 import metrics"
        router_register = "app.include_router(metrics.router)"
    else:
        # Попробуем найти существующий router include
        import re
        m = re.search(r'from ([\w\.]+) import ([\w_]+)', c)
        print(f"Existing import pattern: {m.group(0) if m else 'none'}")
        metrics_import = "from backend.app.api.v1 import metrics"
        router_register = "app.include_router(metrics.router)"
    
    if "metrics.router" not in c:
        # Добавить import после других v1 imports
        lines = c.split('\n')
        new_lines = []
        last_import_idx = -1
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.startswith('from ') and 'import' in line and ('v1' in line or 'api' in line):
                last_import_idx = i
        
        if last_import_idx >= 0:
            new_lines.insert(last_import_idx + 1, metrics_import)
            c = '\n'.join(new_lines)
            print("✅ Import added")
        
        # Добавить include_router после других include_router
        if "app.include_router" in c:
            lines = c.split('\n')
            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip().startswith('app.include_router(') and 'metrics' not in line:
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(' ' * indent + router_register)
            c = '\n'.join(new_lines)
            print("✅ Router registered")
        
        pathlib.Path(main_path).write_text(c, encoding="utf-8")
    else:
        print("ℹ️ metrics.router already registered")

# 2. Fix docker-compose.yml networks
p = pathlib.Path("/app/docker-compose.yml")
config = yaml.safe_load(p.read_text())

# Проверяем какие networks объявлены
declared_networks = list(config.get("networks", {}).keys()) if config.get("networks") else []
print(f"\nDeclared networks: {declared_networks}")

# Проверяем networks у backend
backend_networks = config.get("services", {}).get("backend", {}).get("networks", [])
print(f"Backend networks: {backend_networks}")

# Удаляем amf-network из prometheus/grafana если его нет
for svc in ["prometheus", "grafana"]:
    if svc in config["services"]:
        svc_networks = config["services"][svc].get("networks", [])
        if "amf-network" in svc_networks and "amf-network" not in declared_networks:
            if backend_networks:
                # Используем те же networks что и у backend
                config["services"][svc]["networks"] = list(backend_networks)
                print(f"✅ {svc} networks → {backend_networks}")
            else:
                # Нет networks у backend - убираем вообще
                del config["services"][svc]["networks"]
                print(f"✅ {svc} networks removed (using default)")

p.write_text(yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False))
print("✅ docker-compose.yml fixed")