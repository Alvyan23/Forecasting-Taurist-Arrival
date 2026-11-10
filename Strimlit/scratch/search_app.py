import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/nb_cell8_app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "admin" in line.lower() or "metode" in line.lower() or "evaluasi" in line.lower():
        if any(keyword in line for keyword in ["def ", "st.selectbox", "st.radio", "st.button", "jalankan_metode", "muat_hasil"]):
            print(f"L{i+1}: {line.strip()[:100]}")
