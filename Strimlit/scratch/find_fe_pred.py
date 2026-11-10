import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("forecasting_engine.py", "r", encoding="utf-8") as f:
    text = f.read()

lines = text.splitlines()
for i, l in enumerate(lines):
    if "def jalankan_prediksi" in l:
        print(f"L{i+1}: {l}")
        for j in range(i, min(i+60, len(lines))):
            print(f"{j+1:4d}: {lines[j]}")
        break
