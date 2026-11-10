import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("cell_14.py", encoding="utf-8") as f:
    text = f.read()

lines = text.splitlines()
for i, l in enumerate(lines[:90]):
    print(f"L{i+1}: {l}")
