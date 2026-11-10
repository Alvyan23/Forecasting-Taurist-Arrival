import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("cell_18.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i in range(85, min(180, len(lines))):
    print(f"{i+1}: {lines[i]}", end="")
