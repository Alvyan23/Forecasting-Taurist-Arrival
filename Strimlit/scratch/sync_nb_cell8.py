import json, shutil, time

sys_time = time.strftime("%Y%m%d_%H%M%S")
bak_nb = f"noteboke (1).ipynb.bak_{sys_time}"
shutil.copy("noteboke (1).ipynb", bak_nb)
print(f"Backed up noteboke (1).ipynb to {bak_nb}")

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

with open("app.py", "r", encoding="utf-8") as f:
    app_content = f.read()

cell8_lines = ["%%writefile app.py\n"] + [line + "\n" for line in app_content.splitlines()]
if cell8_lines and cell8_lines[-1].endswith("\n"):
    cell8_lines[-1] = cell8_lines[-1][:-1]

nb["cells"][8]["source"] = cell8_lines

with open("noteboke (1).ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Synchronized Cell 8 in noteboke (1).ipynb successfully!")
