import json, os, shutil

# Load the tested new code
with open("scratch/test_new_admin/admin_methods.py", "r", encoding="utf-8") as f:
    clean_am = f.read()

with open("scratch/test_new_admin/app.py", "r", encoding="utf-8") as f:
    clean_app = f.read()

# Standalone files
with open("admin_methods.py", "w", encoding="utf-8") as f:
    f.write(clean_am)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(clean_app)

print("Updated admin_methods.py and app.py in workspace.")

# Notebook update
with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

nb["cells"][6]["source"] = "%%writefile admin_methods.py\n" + clean_am
nb["cells"][8]["source"] = "%%writefile app.py\n" + clean_app

with open("noteboke (1).ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Updated noteboke (1).ipynb successfully!")
