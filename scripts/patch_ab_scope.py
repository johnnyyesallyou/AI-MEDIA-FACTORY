import pathlib

p = pathlib.Path("/app/core/models/analytics.py")
c = p.read_text(encoding="utf-8")

if "scope = Column" not in c:
    c = c.replace(
        "    traffic_split = Column(JSONB, nullable=False)  # {variant_id: percentage}",
        "    traffic_split = Column(JSONB, nullable=False)  # {variant_id: percentage}\n    scope = Column(JSONB, default=dict)  # {channel_ids: [...], content_type: 'news'}",
        1,
    )
    p.write_text(c, encoding="utf-8")
    print("✅ scope added to ABTest model")
else:
    print("ℹ️ scope already exists")