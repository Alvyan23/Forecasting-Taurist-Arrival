import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/nb_cell6_admin_methods.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(1460, min(len(lines), 1625)):
    print(f"{i+1:4d}: {lines[i]}", end="")
