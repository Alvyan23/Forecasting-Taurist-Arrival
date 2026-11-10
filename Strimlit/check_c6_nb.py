import json

with open("strimlit-skripsi-terbaru (2).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

cell6 = nb["cells"][6]
src = "".join(cell6["source"])
print("Cell 6 type:", cell6["cell_type"])
print("Cell 6 first 3 lines:")
print("\n".join(src.split("\n")[:3]))
print("Cell 6 last 3 lines:")
print("\n".join(src.split("\n")[-3:]))
