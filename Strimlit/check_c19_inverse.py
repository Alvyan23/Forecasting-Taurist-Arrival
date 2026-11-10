import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("cell_19.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, l in enumerate(lines[:60]):
    print(f"{i+1}: {l}", end="")
