import yaml
import pathlib

p = pathlib.Path("docker-compose.yml")
config = yaml.safe_load(p.read_text())

# Добавляем SSL переменные окружения в backend service
if "environment" not in config["services"]["backend"]:
    config["services"]["backend"]["environment"] = []

env_vars = config["services"]["backend"]["environment"]

# Проверяем что уже не добавлено
if not any("SSL_VERIFY" in str(v) for v in env_vars):
    env_vars.extend([
        "SSL_VERIFY=false",
        "PYTHONHTTPSVERIFY=0",
        "CURL_CA_BUNDLE=",
        "REQUESTS_CA_BUNDLE=",
    ])

p.write_text(yaml.dump(config, default_flow_style=False, allow_unicode=True))
print("✅ docker-compose.yml updated with SSL env vars")