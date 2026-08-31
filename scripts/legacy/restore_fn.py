import pathlib, re, subprocess

cur_path = pathlib.Path("frontend/src/pages/Channels.tsx")
cur = cur_path.read_text(encoding="utf-8")

git_ver = subprocess.run(
    ["git", "show", "HEAD:frontend/src/pages/Channels.tsx"],
    capture_output=True, text=True
).stdout

m = re.search(r"  const loadChannels = async \(\) => \{[\s\S]*?\n  \};", git_ver)
if not m:
    print("[FAIL] loadChannels not found in git HEAD")
    raise SystemExit(1)

block = m.group(0)
print("[i] extracted loadChannels from git:", len(block.splitlines()), "lines")

if "const loadChannels = async" not in cur:
    anchor = "  const loadTemplates = async () => {"
    assert anchor in cur, "anchor not found"
    cur = cur.replace(anchor, block + "\n\n" + anchor, 1)
    cur_path.write_text(cur, encoding="utf-8")
    print("[OK] loadChannels restored")
else:
    print("[i] loadChannels already present")

for name in ["loadChannels", "loadTemplates", "handleCreateFromTemplate", "templateCreating"]:
    print(f"  {name}: {cur.count(name)} refs")
print("  setShowTemplateModal refs:", cur.count("setShowTemplateModal"))