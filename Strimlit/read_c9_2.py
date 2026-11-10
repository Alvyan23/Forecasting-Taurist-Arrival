import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("cell_9.py", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines[120:200]):
    print(f"{i+121}: {l}", end="")
