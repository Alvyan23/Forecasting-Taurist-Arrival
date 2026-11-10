with open('admin_methods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'benchmark' in line.lower() and 'def ' in line:
        print(f"{i+1}: {lines[i].strip()}")
