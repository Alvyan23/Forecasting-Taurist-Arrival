import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("forecasting_engine.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(250, 275):
    print(f"{i+1}: {lines[i][:100]}")
