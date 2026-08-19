import yaml, pathlib

p = pathlib.Path("/app/docker-compose.yml")
cfg = yaml.safe_load(p.read_text(encoding="utf-8"))

changed = []
for svc in ("frontend", "nginx"):
    s = cfg["services"].get(svc)
    if s is None:
        continue
    nets = s.get("networks") or []
    if "amf_network" not in nets:
        s["networks"] = (nets if isinstance(nets, list) else list(nets)) + ["amf_network"]
        changed.append(svc)

p.write_text(yaml.dump(cfg, sort_keys=False, default_flow_style=False, allow_unicode=True), encoding="utf-8")
print(f"networks fixed for: {changed or 'already ok'}")