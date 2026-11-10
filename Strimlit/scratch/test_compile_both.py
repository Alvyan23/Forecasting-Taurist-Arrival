with open("scratch/test_tab_render/admin_methods.py", "r", encoding="utf-8") as f:
    c_am = f.read()

with open("scratch/test_tab_render/app.py", "r", encoding="utf-8") as f:
    c_app = f.read()

compile(c_am, "admin_methods.py", "exec")
compile(c_app, "app.py", "exec")

print("Both files compile with 0 syntax errors!")
