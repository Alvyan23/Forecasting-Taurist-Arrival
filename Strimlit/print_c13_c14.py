import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=== CELL 13 ===")
with open("cell_13.py", "r", encoding="utf-8") as f:
    print(f.read())

print("=== CELL 14 (PLOTS) ===")
with open("cell_14.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if "plt." in l or "savefig" in l or "subplot" in l:
        print(f"{i+1}: {l.strip()}")
