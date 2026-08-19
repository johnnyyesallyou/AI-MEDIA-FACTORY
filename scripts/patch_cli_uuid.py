import pathlib

p = pathlib.Path("/app/core/cli.py")
c = p.read_text(encoding="utf-8")

# Меняем --channel-id с type=int на type=str
old = '    optimize_parser.add_argument("--channel-id", type=int, help="Channel ID for optimization")'
new = '    optimize_parser.add_argument("--channel-id", type=str, help="Channel ID (UUID) for optimization")'
if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] CLI channel-id fixed to str")
else:
    print("[i] already correct or different format")