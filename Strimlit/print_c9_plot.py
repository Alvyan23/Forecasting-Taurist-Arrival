import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("cell_9.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "fig, axes = plt.subplots" in l:
        for j in range(i, min(i+35, len(lines))):
            print(f"{j+1}: {lines[j]}", end="")
        break
