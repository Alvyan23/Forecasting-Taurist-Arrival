import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    l = line.lower()
    if 'render_hasil' in l or 'admin_methods' in l or 'def admin_page' in l:
        print(f"{i+1}: {line.strip()}")
