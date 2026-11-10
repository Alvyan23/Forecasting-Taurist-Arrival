import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("cell_10.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "plt." in l or "savefig" in l or "subplot" in l:
        print(f"{i+1}: {l.strip()}")
