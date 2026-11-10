import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("cell_19.py", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines[120:220]):
    print(f"L{i+121}: {l}", end="")
