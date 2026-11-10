import json

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for i, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    if "admin_methods.py" in src or "app.py" in src or "%%writefile" in src:
        first_line = cell.get("source", [""])[0].strip() if cell.get("source") else ""
        print(f"Cell {i}: {first_line[:80]} (length: {len(src)})")
