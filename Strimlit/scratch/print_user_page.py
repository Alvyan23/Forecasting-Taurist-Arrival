import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/nb_cell8_app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(909, 986):
    print(f"{i+1:4d}: {lines[i]}", end="")
