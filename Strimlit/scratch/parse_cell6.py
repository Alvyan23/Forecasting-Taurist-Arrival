import re

with open("scratch/nb_cell6_admin_methods.py", "r", encoding="utf-8") as f:
    text = f.read()

# Let's find function definitions
funcs = re.findall(r'^(def\s+[a-zA-Z0-9_]+\s*\(.*?\):)', text, re.MULTILINE)
for fn in funcs:
    print(fn)

print("\n--- Summary of text ---")
print(f"Length of cell 6: {len(text)} chars, {len(text.splitlines())} lines")
