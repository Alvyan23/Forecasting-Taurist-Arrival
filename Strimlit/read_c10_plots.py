import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("cell_10.py", encoding="utf-8") as f:
    text = f.read()

# search for plt. in cell_10
lines = text.splitlines()
for i, l in enumerate(lines):
    if "plt." in l or "fig," in l or "sns." in l:
        print(f"L{i+1}: {l}")
