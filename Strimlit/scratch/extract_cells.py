import json

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Cell 6 is admin_methods.py
cell6 = "".join(nb["cells"][6]["source"])
with open("scratch/nb_cell6_admin_methods.py", "w", encoding="utf-8") as f:
    f.write(cell6)

# Cell 8 is app.py
cell8 = "".join(nb["cells"][8]["source"])
with open("scratch/nb_cell8_app.py", "w", encoding="utf-8") as f:
    f.write(cell8)

print("Saved cell 6 and cell 8 to scratch.")
