import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

with open("scratch/nb_cell6_admin_methods.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(k in line.lower() for k in ["evaluasi", "menu_tahapan", "render_hasil_admin", "jalankan_metode"]):
        print(f"L{i+1}: {line.strip()[:100]}")
