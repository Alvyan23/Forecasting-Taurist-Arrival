import json, shutil, time, os

ts = time.strftime("%Y%m%d_%H%M%S")
bak_nb = f"noteboke (1).ipynb.bak_{ts}"
shutil.copy("noteboke (1).ipynb", bak_nb)
print(f"Backed up noteboke (1).ipynb to {bak_nb}")

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Read admin_methods.py
with open("admin_methods.py", "r", encoding="utf-8") as f:
    adm_content = f.read()

# Format lines for Cell 6
cell6_lines = ["%%writefile admin_methods.py\n"] + [line + "\n" for line in adm_content.splitlines()]
# If last line was empty or splitlines stripped it, make sure last line has no extra \n or matches standard
if cell6_lines and cell6_lines[-1].endswith("\n"):
    cell6_lines[-1] = cell6_lines[-1][:-1]

nb["cells"][6]["source"] = cell6_lines
print("Updated Cell 6 with admin_methods.py, line count:", len(cell6_lines))

# Read app.py
with open("app.py", "r", encoding="utf-8") as f:
    app_content = f.read()

cell8_lines = ["%%writefile app.py\n"] + [line + "\n" for line in app_content.splitlines()]
if cell8_lines and cell8_lines[-1].endswith("\n"):
    cell8_lines[-1] = cell8_lines[-1][:-1]

nb["cells"][8]["source"] = cell8_lines
print("Updated Cell 8 with app.py, line count:", len(cell8_lines))

with open("noteboke (1).ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Saved noteboke (1).ipynb successfully!")
