import json

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx in [6, 8]:
    print(f"Cell {idx} first 3 lines:")
    for line in nb["cells"][idx]["source"][:3]:
        print("  ", repr(line))
