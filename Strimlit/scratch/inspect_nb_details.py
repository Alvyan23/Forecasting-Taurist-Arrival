import json

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, cell in enumerate(nb["cells"]):
    print(f"\n--- Cell {i} ({cell.get('cell_type')}) ---")
    source = "".join(cell.get("source", []))
    lines = source.split("\n")
    print(f"Lines count: {len(lines)}")
    for line in lines[:10]:
        print("  " + line)
    if len(lines) > 10:
        print("  ...")
