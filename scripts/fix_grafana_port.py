import yaml
import pathlib

p = pathlib.Path("/app/docker-compose.yml")
config = yaml.safe_load(p.read_text())

# Grafana: меняем порт с 3001 на 3002
if "grafana" in config["services"]:
    ports = config["services"]["grafana"].get("ports", [])
    new_ports = []
    for port in ports:
        if str(port).startswith("3001"):
            new_ports.append(port.replace("3001", "3002"))
        else:
            new_ports.append(port)
    config["services"]["grafana"]["ports"] = new_ports
    print(f"✅ Grafana ports: {new_ports}")

p.write_text(yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False))