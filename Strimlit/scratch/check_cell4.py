import json

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

cell4 = "".join(nb["cells"][4]["source"])
if cell4.startswith("%%writefile"):
    c4_code = cell4.split("\n", 1)[1]
else:
    c4_code = cell4

try:
    compile(c4_code, "forecasting_engine.py", "exec")
    print("Cell 4 (forecasting_engine.py) compiles cleanly!")
except Exception as e:
    print(f"Cell 4 compilation error: {e}")
