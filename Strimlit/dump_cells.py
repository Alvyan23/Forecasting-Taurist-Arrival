import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
nb = json.load(open('ICEEMDAN-VMD-GRU/Makam Syaikhona Kholil/iceemdan-vmd-gru-2-journal (syaicona colil)2.ipynb', encoding='utf-8'))

for cell_idx in [6, 9, 10, 13, 14, 18, 19]:
    src = nb['cells'][cell_idx]['source']
    text = ''.join(src) if isinstance(src, list) else str(src)
    with open(f"cell_{cell_idx}.py", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Cell {cell_idx} written ({len(text)} chars)")
