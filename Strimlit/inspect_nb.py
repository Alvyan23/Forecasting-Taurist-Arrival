import json

with open("strimlit-skripsi-terbaru (2).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print("Total cells:", len(nb["cells"]))
for idx, c in enumerate(nb["cells"]):
    src = "".join(c.get("source", []))
    first_line = src.strip().split("\n")[0] if src.strip() else "(empty)"
    print(f"Cell {idx} ({c['cell_type']}): length={len(src)}, first_line={first_line[:70]}")
