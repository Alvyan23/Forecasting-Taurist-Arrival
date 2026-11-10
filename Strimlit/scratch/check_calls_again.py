with open("admin_methods.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "_render_detail_notebook" in line:
            print(f"Line {i+1}: {line.strip()}")
