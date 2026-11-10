"""Sync notebook cells 6 and 8 with the updated admin_methods.py and app.py."""
import json, re

NB = "c:/Users/TOSHIBA/Documents/SIstem Informasi/Skripsi/Draft Skripsi/FORECASTING/Strimlit/strimlit-skripsi-terbaru (2).ipynb"

with open(NB, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Read updated files
with open("c:/Users/TOSHIBA/Documents/SIstem Informasi/Skripsi/Draft Skripsi/FORECASTING/Strimlit/admin_methods.py", 'r', encoding='utf-8') as f:
    admin_src = f.read()

with open("c:/Users/TOSHIBA/Documents/SIstem Informasi/Skripsi/Draft Skripsi/FORECASTING/Strimlit/app.py", 'r', encoding='utf-8') as f:
    app_src = f.read()

def to_cell_source(header, content):
    """Convert file content to notebook cell source list."""
    lines = (header + "\n" + content).splitlines(keepends=True)
    return lines

# Find cells by first-line content
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell['source'])
    if cell['cell_type'] == 'code' and '%%writefile admin_methods.py' in src[:50]:
        print(f"Cell {i}: admin_methods.py (len={len(src)})")
        new_src = "%%writefile admin_methods.py\n" + admin_src
        nb['cells'][i]['source'] = [line if line.endswith('\n') else line+'\n' 
                                     for line in new_src.splitlines()]
        print(f"  -> Updated to {len(new_src)} chars")
    elif cell['cell_type'] == 'code' and '%%writefile app.py' in src[:30]:
        print(f"Cell {i}: app.py (len={len(src)})")
        new_src = "%%writefile app.py\n" + app_src
        nb['cells'][i]['source'] = [line if line.endswith('\n') else line+'\n'
                                     for line in new_src.splitlines()]
        print(f"  -> Updated to {len(new_src)} chars")

with open(NB, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Notebook updated OK")
