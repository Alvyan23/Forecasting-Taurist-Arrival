import json, shutil, os, time

ts = time.strftime("%Y%m%d_%H%M%S")
shutil.copy2("noteboke (1).ipynb", f"noteboke (1).ipynb.bak_{ts}")
shutil.copy2("admin_methods.py", f"admin_methods.py.bak_{ts}")
shutil.copy2("app.py", f"app.py.bak_{ts}")

print(f"Backups created with timestamp {ts}")

with open("scratch/test_tab_render/admin_methods.py", "r", encoding="utf-8") as f:
    clean_am = f.read()

with open("scratch/test_tab_render/app.py", "r", encoding="utf-8") as f:
    clean_app = f.read()

# Update workspace files
with open("admin_methods.py", "w", encoding="utf-8") as f:
    f.write(clean_am)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(clean_app)

print("Updated admin_methods.py and app.py in workspace.")

# Update noteboke (1).ipynb
with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

nb["cells"][6]["source"] = "%%writefile admin_methods.py\n" + clean_am
nb["cells"][8]["source"] = "%%writefile app.py\n" + clean_app

with open("noteboke (1).ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Updated noteboke (1).ipynb successfully!")
