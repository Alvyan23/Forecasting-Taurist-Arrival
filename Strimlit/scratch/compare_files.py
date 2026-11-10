import difflib

for orig, nb_ver in [("admin_methods.py", "scratch/nb_cell6_admin_methods.py"), ("app.py", "scratch/nb_cell8_app.py")]:
    with open(orig, "r", encoding="utf-8") as f:
        t_orig = f.read()
    with open(nb_ver, "r", encoding="utf-8") as f:
        t_nb = f.read()
    # strip %%writefile line from notebook version
    if t_nb.startswith("%%writefile"):
        t_nb = t_nb.split("\n", 1)[1]
    diff = list(difflib.unified_diff(t_orig.splitlines(), t_nb.splitlines()))
    print(f"Diff between {orig} and notebook version: {len(diff)} lines of diff")
    if diff:
        print("\n".join(diff[:30]))
