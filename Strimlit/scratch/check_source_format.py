import json

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx in [6, 8]:
    src = nb["cells"][idx]["source"]
    print(f"Cell {idx} source type: {type(src)}, length: {len(src)}")
    print(f"  First 3 items: {src[:3]}")
    print(f"  Ends with newline? {[s.endswith(chr(10)) for s in src[:3]]}")
