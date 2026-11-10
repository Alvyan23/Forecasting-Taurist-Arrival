import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/nb_cell8_app.py", "r", encoding="utf-8") as f:
    text = f.read()

# Let's see all page functions in app.py
lines = text.splitlines()
for i, l in enumerate(lines):
    if l.startswith("def ") and "_page" in l:
        print(f"L{i+1}: {l}")
