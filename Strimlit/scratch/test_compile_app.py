with open("scratch/test_new_admin/app.py", "r", encoding="utf-8") as f:
    code = f.read()

try:
    compile(code, "app.py", "exec")
    print("scratch/test_new_admin/app.py compiled cleanly with no syntax errors!")
except Exception as e:
    print(f"Compilation error: {e}")
