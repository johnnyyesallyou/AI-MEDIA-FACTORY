import yaml
import pathlib

p = pathlib.Path("docker-compose.yml")
config = yaml.safe_load(p.read_text())

# Добавляем Prometheus service
if "prometheus" not in config["services"]:
    config["services"]["prometheus"] = {
        "image": "prom/prometheus:v2.45.0",
        "container_name": "amf_prometheus",
        "ports": ["9090:9090"],
        "volumes": [
            "./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro",
            "./monitoring/prometheus/alert_rules.yml:/etc/prometheus/alert_rules.yml:ro",
            "prometheus_data:/prometheus"
        ],
        "command": [
            "--config.file=/etc/prometheus/prometheus.yml",
            "--storage.tsdb.path=/prometheus",
            "--storage.tsdb.retention.time=15d"
        ],
        "restart": "unless-stopped",
        "networks": ["amf-network"]
    }

# Добавляем Grafana service
if "grafana" not in config["services"]:
    config["services"]["grafana"] = {
        "image": "grafana/grafana:10.0.0",
        "container_name": "amf_grafana",
        "ports": ["3001:3000"],
        "environment": [
            "GF_SECURITY_ADMIN_PASSWORD=admin123",
            "GF_USERS_ALLOW_SIGN_UP=false"
        ],
        "volumes": [
            "./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro",
            "./monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro",
            "grafana_data:/var/lib/grafana"
        ],
        "restart": "unless-stopped",
        "networks": ["amf-network"]
    }

# Volumes
if "volumes" not in config:
    config["volumes"] = {}
config["volumes"]["prometheus_data"] = {}
config["volumes"]["grafana_data"] = {}

p.write_text(yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False))
print("✅ docker-compose.yml updated with Prometheus + Grafana")