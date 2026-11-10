with open('admin_methods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def render_tahap_praproses' in line:
        for j in range(i, i+15):
            print(f"{j+1}: {lines[j].strip()}")
        break
