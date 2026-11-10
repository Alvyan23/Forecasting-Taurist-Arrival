import shutil, os, time

ts = time.strftime("%Y%m%d_%H%M%S")
shutil.copy2("noteboke (1).ipynb", f"noteboke (1).ipynb.bak_{ts}")
shutil.copy2("admin_methods.py", f"admin_methods.py.bak_{ts}")
shutil.copy2("app.py", f"app.py.bak_{ts}")

print("Backups created:")
print(f"  noteboke (1).ipynb.bak_{ts}")
print(f"  admin_methods.py.bak_{ts}")
print(f"  app.py.bak_{ts}")
