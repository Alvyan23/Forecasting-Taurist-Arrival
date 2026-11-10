import json

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print("Cell 6 joined first 100 chars:", repr("".join(nb["cells"][6]["source"][:100])))
print("Cell 8 joined first 100 chars:", repr("".join(nb["cells"][8]["source"][:100])))
