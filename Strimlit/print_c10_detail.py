import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("cell_10.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for j in range(180, 246):
    print(f"{j+1}: {lines[j]}", end="")
