import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("cell_10.py", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines[175:250]):
    print(f"{i+176}: {l}", end="")
