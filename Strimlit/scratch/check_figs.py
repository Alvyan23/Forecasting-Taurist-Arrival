import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/nb_cell6_admin_methods.py", "r", encoding="utf-8") as f:
    text = f.read()

lines = text.splitlines()
for i, l in enumerate(lines):
    if "def fig_aktual_prediksi" in l or "def fig_masa_depan" in l:
        print(f"L{i+1}: {l}")
        for j in range(i, min(i+35, len(lines))):
            print(f"{j+1:4d}: {lines[j]}")
