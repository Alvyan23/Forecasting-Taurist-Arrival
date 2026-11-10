import json

with open("strimlit-skripsi-terbaru (2).ipynb", "r", encoding="utf-8") as f:
    nb2 = json.load(f)

print(f"Total cells in strimlit-skripsi-terbaru (2).ipynb: {len(nb2['cells'])}")
for i, cell in enumerate(nb2["cells"]):
    print(f"\n--- Cell {i} ({cell.get('cell_type')}) ---")
    source = "".join(cell.get("source", []))
    lines = source.split("\n")
    print(f"Lines count: {len(lines)}")
    for line in lines[:5]:
        print("  " + line)
