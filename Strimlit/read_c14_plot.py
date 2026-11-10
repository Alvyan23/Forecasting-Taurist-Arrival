import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("cell_14.py", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines[90:150]):
    print(f"L{i+91}: {l}", end="")
