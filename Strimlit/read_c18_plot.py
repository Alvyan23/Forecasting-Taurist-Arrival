import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("cell_18.py", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines[120:230]):
    print(f"L{i+121}: {l}", end="")
