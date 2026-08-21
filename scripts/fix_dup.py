import pathlib

p = pathlib.Path("frontend/src/pages/Channels.tsx")
lines = p.read_text(encoding="utf-8").split("\n")

idxs = [i for i, l in enumerate(lines) if "const loadTemplates = async" in l]
print(f"loadTemplates declarations found: {len(idxs)} at lines {[i+1 for i in idxs]}")

if len(idxs) >= 2:
    first, second = idxs[0], idxs[1]
    # удаляем старый блок: от первой loadTemplates до второй (не включая)
    del lines[first:second]
    p.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] removed old block lines {first+1}..{second}")
else:
    print("[!] expected 2 declarations")

c = "\n".join(lines)
print("setShowTemplateModal refs left:", c.count("setShowTemplateModal"))
print("loadTemplates refs now:", c.count("const loadTemplates = async"))