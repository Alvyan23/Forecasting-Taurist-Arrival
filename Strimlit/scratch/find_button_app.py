import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    l_low = line.lower()
    if any(k in l_low for k in ["mulai prediksi", "button", "st.button", "submitted", "hasil_admin", "session_state"]):
        if any(w in l_low for w in ["prediksi", "hasil", "btn", "submit", "run", "mulai"]):
            print(f"{i+1}: {line.strip()[:100]}")
